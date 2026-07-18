# Repository Quality Controls

These controls protect the public repository and improve source quality. They
are development safeguards, not part of the server-build architecture or its
presentation material.

## Enforced checks

The repository hygiene scanner checks tracked source files and readable XML
inside PowerPoint, Word, Excel, and Visio artifacts. It blocks:

- Windows, WSL, Linux, and macOS user-home paths
- checkout-owner and local runtime usernames discovered without storing them
- prohibited organization identifiers represented by one-way hashes
- high-confidence private keys and service-token formats
- invalid UTF-8, non-breaking or zero-width characters, and common mojibake
- internal AI citation markers, transcript role tags, and AI self-references
- Markdown residue such as prose backslashes, escaped emphasis, and excess
  trailing spaces outside code fences

The blocked-token policy stores only lowercase SHA-256 digests in
`.quality-policy.json`. The sensitive source value is not committed. Add a new
digest only when a term must be prohibited across all public content.

For additional CI-only identity values, define the optional GitHub Actions
secret `REPOSITORY_BLOCKED_TOKEN_HASHES` as comma-separated lowercase SHA-256
digests. The workflow passes those digests to the scanner without exposing the
source values in the repository.

The checks intentionally do not ban valid Unicode punctuation, architectural
language about AI, synthetic credentials, or generic product names.

## Local hooks

Install the development dependencies and both Git hooks:

```bash
python3 -m pip install --requirement requirements-dev.txt
pre-commit install --hook-type pre-commit --hook-type pre-push
```

The pre-commit hook scans changed files and validates catalog fixtures when
they are affected. The pre-push hook runs the complete validation suite,
including Molecule when it is installed.

Run the controls directly at any time:

```bash
python3 scripts/check_repository_hygiene.py --all
bash scripts/validate.sh
```

## Continuous integration

`.github/workflows/quality.yml` repeats the hygiene scan and complete automation
validation for pull requests and pushes to `main`. Local hooks improve feedback
time; CI is the authoritative gate because local hooks can be bypassed.

Privacy, secret, and encoding findings are blocking. Resolve the source rather
than excluding a presentable file from inspection.
