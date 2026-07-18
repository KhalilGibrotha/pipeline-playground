from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_repository_hygiene as hygiene  # noqa: E402


class RepositoryHygieneTests(unittest.TestCase):
    def rules_for(self, text: str, blocked_hashes: dict[str, str] | None = None) -> set[str]:
        findings = hygiene.check_text(text, "fixture.txt", blocked_hashes or {})
        return {finding.rule for finding in findings}

    def test_blocks_common_local_home_paths(self) -> None:
        fixtures = (
            "C:" + "\\Users\\" + "example-user\\repo",
            "/mnt/c/" + "Users/" + "example-user/repo",
            "/" + "home/" + "example-user/repo",
            "/" + "Users/" + "example-user/repo",
        )
        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                self.assertIn("local-path", self.rules_for(fixture))

    def test_blocks_hashed_policy_token_without_storing_it(self) -> None:
        source_value = "".join(chr(value) for value in (115, 101, 99, 117))
        digest = hygiene.token_digest(source_value)
        findings = hygiene.check_text(source_value, "fixture.txt", {digest: "policy token"})
        self.assertEqual([finding.rule for finding in findings], ["blocked-token"])

    def test_discovers_checkout_owner_without_storing_the_username(self) -> None:
        synthetic_identity = "quality-fixture-user"
        with mock.patch.dict(
            hygiene.os.environ,
            {"USER": synthetic_identity, "USERNAME": "", "LOGNAME": ""},
        ):
            discovered = hygiene.discover_local_identity_hashes()

        self.assertIn(hygiene.token_digest(synthetic_identity), discovered)
        self.assertTrue(all(len(digest) == 64 for digest in discovered))

    def test_blocks_mojibake_and_ai_citation_residue(self) -> None:
        mojibake = chr(0x00E2) + chr(0x20AC) + chr(0x2122)
        citation = "turn" + "12search4"
        self.assertIn("mojibake", self.rules_for(mojibake))
        self.assertIn("ai-artifact", self.rules_for(citation))

    def test_accepts_xml_byte_order_mark_at_start(self) -> None:
        self.assertEqual(self.rules_for("\ufeff<?xml version='1.0'?>"), set())

    def test_blocks_markdown_generation_residue_outside_code_fences(self) -> None:
        artifact = "Prose with escaped\\_emphasis\\\n"
        rules = {finding.rule for finding in hygiene.check_markdown_artifacts(artifact, "fixture.md")}
        self.assertEqual(rules, {"markdown-artifact"})

        code_sample = "```bash\ncommand \\\n+  --option value\n```\n"
        self.assertEqual(hygiene.check_markdown_artifacts(code_sample, "fixture.md"), [])


if __name__ == "__main__":
    unittest.main()
