# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Formalizes the ad-hoc secret_scanner checks run manually earlier this
session (URL false positive, backtick-filename false positive, real
secret still caught) into a real, re-runnable regression suite instead
of a one-off verification that leaves no lasting check.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from llmos_toolkit.plugins.secret_scanner.plugin import scan_file


class TestSecretScannerRegression(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _scan(self, name: str, content: str):
        p = self.root / name
        p.write_text(content)
        return scan_file(p, self.root)

    def test_long_url_not_flagged_as_high_entropy(self):
        findings = self._scan("doc.md", "See https://wandb.ai/report/VmlldzoxMTMxNjQ4NA-some-long-path-segment for details.\n")
        entropy_hits = [f for f in findings if f["type"] == "High Entropy Token"]
        self.assertEqual(entropy_hits, [], "URL path segments should not be flagged as high-entropy secrets")

    def test_long_backtick_filename_not_flagged(self):
        findings = self._scan("doc.md", "See `chatgpt-com-share-6a78d50f-f114-83ea-b2e0-77f3ddba9f3c-ogimg.md` for the export.\n")
        entropy_hits = [f for f in findings if f["type"] == "High Entropy Token"]
        self.assertEqual(entropy_hits, [], "long filenames in backticks should not be flagged as high-entropy secrets")

    def test_real_api_key_still_caught_outside_url_or_backtick(self):
        findings = self._scan("config.py", 'API_KEY = "sk-thisIsAFakeHighEntropySecretTokenForTest12345"\n')
        types = {f["type"] for f in findings}
        self.assertIn("API Key", types)
        self.assertIn("OpenAI-style Key", types)

    def test_real_key_inside_backticks_still_caught_by_named_pattern(self):
        """The entropy check is excluded inside backticks; the named
        regex patterns (API Key etc.) are NOT -- this must still catch
        a real credential someone pastes in markdown code formatting."""
        findings = self._scan("doc.md", "config: `API_KEY=sk-realistictestkey1234567890abcdefgh`\n")
        types = {f["type"] for f in findings}
        self.assertTrue({"API Key", "OpenAI-style Key"} & types, "named-pattern checks must still fire inside backticks")

    def test_sensitive_filename_still_flagged(self):
        findings = self._scan(".env", "PLACEHOLDER=1\n")
        types = {f["type"] for f in findings}
        self.assertIn("Sensitive File Name", types)

    def test_env_example_not_flagged_by_filename(self):
        findings = self._scan(".env.example", "ANTHROPIC_API_KEY=\nOPENAI_API_KEY=\n")
        types = {f["type"] for f in findings}
        self.assertNotIn("Sensitive File Name", types, ".env.example is a template by convention, never a real secret")

    def test_env_example_still_content_scanned(self):
        """Template-suffix exemption is filename-only -- a real key
        accidentally left in a .env.example must still be caught."""
        findings = self._scan(".env.example", 'ANTHROPIC_API_KEY="sk-realistictestkey1234567890abcdefgh"\n')
        types = {f["type"] for f in findings}
        self.assertTrue(types - {"Sensitive File Name"}, "content-based checks must still run on template files")


if __name__ == "__main__":
    unittest.main()
