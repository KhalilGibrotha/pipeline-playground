#!/usr/bin/env python3
"""Block local identity leaks, encoding damage, secrets, and AI artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / ".quality-policy.json"

TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".css",
    ".csv",
    ".devfile",
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    ".html",
    ".ini",
    ".j2",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
OFFICE_SUFFIXES = {".docx", ".pptx", ".xlsx", ".vsdx"}
OFFICE_TEXT_SUFFIXES = {".xml", ".rels", ".txt", ".json"}
GENERIC_RUNTIME_USERS = {
    "coder",
    "codespace",
    "ec2-user",
    "gitlab-runner",
    "root",
    "runner",
    "ubuntu",
    "vscode",
}

HOME_SEGMENT = "home"
USERS_SEGMENT = "users"
LOCAL_PATH_PATTERNS = (
    re.compile(r"(?i)(?:[a-z]:|file:/+)[\\/]" + USERS_SEGMENT + r"[\\/][^\\/\s\"'<>]+"),
    re.compile(r"(?i)/mnt/[a-z]/" + USERS_SEGMENT + r"/[^/\s\"'<>]+"),
    re.compile(r"(?i)/(?:" + HOME_SEGMENT + "|" + USERS_SEGMENT + r")/[^/\s\"'<>]+"),
    re.compile(
        r"(?i)\\\\wsl(?:\.localhost)?\$\\[^\\]+\\"
        + HOME_SEGMENT
        + r"\\[^\\\s\"'<>]+"
    ),
)

SECRET_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
)

AI_ARTIFACT_PATTERNS = (
    ("AI self-reference", re.compile(r"\bas an " + r"AI language model\b", re.IGNORECASE)),
    ("chat transcript role marker", re.compile(r"^\s*<(?:assistant|analysis|commentary|final)>\s*$", re.IGNORECASE)),
    ("internal web citation", re.compile(r"turn\d+(?:search|fetch|view|open)\d+", re.IGNORECASE)),
    ("internal citation marker", re.compile(chr(0xE200) + r"cite")),
    ("OpenAI citation residue", re.compile(r"contentReference\[oaicite:", re.IGNORECASE)),
    (
        "AI generator attribution",
        re.compile(r"\b(?:generated (?:by|with)|co-authored-by:) " + r"(?:ChatGPT|Claude)\b", re.IGNORECASE),
    ),
)

MOJIBAKE_FRAGMENTS = (
    chr(0x00E2) + chr(0x20AC),
    chr(0x00C3),
    chr(0x00C2) + chr(0x00A0),
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    detail: str


def tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    return [REPO_ROOT / item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def normalize_paths(values: Iterable[str]) -> list[Path]:
    paths: list[Path] = []
    for value in values:
        path = Path(value)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if path.is_file():
            paths.append(path.resolve())
    return sorted(set(paths))


def token_digest(value: str) -> str:
    return hashlib.sha256(value.casefold().encode("utf-8")).hexdigest()


def discover_local_identity_hashes() -> dict[str, str]:
    candidates: set[str] = set()
    parts = REPO_ROOT.parts
    for index, part in enumerate(parts[:-1]):
        if part.casefold() in {HOME_SEGMENT, USERS_SEGMENT}:
            candidates.add(parts[index + 1])

    for variable in ("USER", "USERNAME", "LOGNAME"):
        if value := os.environ.get(variable):
            candidates.add(value)

    return {
        token_digest(candidate): "local checkout or runtime username"
        for candidate in candidates
        if candidate.casefold() not in GENERIC_RUNTIME_USERS
        and re.fullmatch(r"[A-Za-z0-9._-]{3,}", candidate)
    }


def load_blocked_hashes() -> dict[str, str]:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    blocked = {
        item["sha256"].lower(): item["reason"]
        for item in policy.get("blocked_token_sha256", [])
    }
    blocked.update(discover_local_identity_hashes())

    external_hashes = os.environ.get("REPOSITORY_BLOCKED_TOKEN_HASHES", "")
    for digest in re.split(r"[,;\s]+", external_hashes):
        if re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            blocked[digest.lower()] = "externally configured prohibited identifier"
    return blocked


def display_path(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def check_text(text: str, location: str, blocked_hashes: dict[str, str]) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()

    for number, line in enumerate(lines, 1):
        if number == 1 and line.startswith("\ufeff"):
            line = line.removeprefix("\ufeff")

        for pattern in LOCAL_PATH_PATTERNS:
            if match := pattern.search(line):
                findings.append(Finding(location, number, "local-path", match.group(0)))

        for name, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(Finding(location, number, "secret", name))

        for name, pattern in AI_ARTIFACT_PATTERNS:
            if pattern.search(line):
                findings.append(Finding(location, number, "ai-artifact", name))

        if "\ufffd" in line:
            findings.append(Finding(location, number, "encoding", "Unicode replacement character"))
        if "\u00a0" in line:
            findings.append(Finding(location, number, "encoding", "non-breaking space"))
        if "\u200b" in line or "\ufeff" in line:
            findings.append(Finding(location, number, "encoding", "zero-width character"))
        if any(fragment in line for fragment in MOJIBAKE_FRAGMENTS):
            findings.append(Finding(location, number, "mojibake", "likely mis-decoded UTF-8"))

        for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9._-]{2,}", line):
            digest = token_digest(token)
            if digest in blocked_hashes:
                findings.append(Finding(location, number, "blocked-token", blocked_hashes[digest]))

    return findings


def check_markdown_artifacts(text: str, location: str) -> list[Finding]:
    findings: list[Finding] = []
    in_code_fence = False
    in_front_matter = text.startswith("---\n")

    for number, line in enumerate(text.splitlines(), 1):
        if in_front_matter:
            if number > 1 and line == "---":
                in_front_matter = False
            continue

        if line.lstrip().startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        prose = re.sub(r"`[^`]*`", "", line)
        if re.search(r" {3,}$", line):
            findings.append(Finding(location, number, "markdown-artifact", "three or more trailing spaces"))
        if line.endswith("\\"):
            findings.append(Finding(location, number, "markdown-artifact", "trailing prose backslash"))
        if re.search(r"(?<!\\)\\[_*]", prose):
            findings.append(Finding(location, number, "markdown-artifact", "escaped prose emphasis character"))

    return findings


def check_plain_file(path: Path, blocked_hashes: dict[str, str]) -> list[Finding]:
    location = display_path(path)
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        return [Finding(location, 1, "encoding", f"not valid UTF-8 at byte {error.start}")]

    findings = check_text(text, location, blocked_hashes)
    if path.suffix.lower() == ".md":
        findings.extend(check_markdown_artifacts(text, location))
    if raw and not raw.endswith(b"\n"):
        findings.append(Finding(location, len(text.splitlines()) or 1, "format", "missing final newline"))
    return findings


def check_office_file(path: Path, blocked_hashes: dict[str, str]) -> list[Finding]:
    findings: list[Finding] = []
    try:
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                if Path(member.filename).suffix.lower() not in OFFICE_TEXT_SUFFIXES:
                    continue
                try:
                    text = archive.read(member).decode("utf-8")
                except UnicodeDecodeError:
                    continue
                location = f"{display_path(path)}!{member.filename}"
                findings.extend(check_text(text, location, blocked_hashes))
    except zipfile.BadZipFile:
        findings.append(Finding(display_path(path), 1, "format", "invalid Office archive"))
    return findings


def check_path(path: Path, blocked_hashes: dict[str, str]) -> list[Finding]:
    suffix = path.suffix.lower()
    if suffix in OFFICE_SUFFIXES:
        return check_office_file(path, blocked_hashes)
    if suffix in TEXT_SUFFIXES or path.name in {"Containerfile", "LICENSE", "Makefile"}:
        return check_plain_file(path, blocked_hashes)
    return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="scan every tracked file")
    parser.add_argument("paths", nargs="*", help="specific files, normally supplied by pre-commit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = tracked_paths() if args.all or not args.paths else normalize_paths(args.paths)
    blocked_hashes = load_blocked_hashes()
    findings = [finding for path in paths for finding in check_path(path, blocked_hashes)]

    if findings:
        for finding in findings:
            print(f"{finding.path}:{finding.line}: [{finding.rule}] {finding.detail}")
        print(f"Repository hygiene failed with {len(findings)} finding(s).", file=sys.stderr)
        return 1

    print(f"Repository hygiene passed for {len(paths)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
