# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import llmos_toolkit.adaptive_drift_logger as adl


class TestAdaptiveDriftLoggerHeaderParsing(unittest.TestCase):
    """Real regression tests for a genuine bug found during a
    housekeeping pass, 2026-08-25: HEADER_RE only captured the integer
    prefix of a decimal section number (5.5 parsed as number='5', with
    the rest of '5.5. Title' becoming a corrupted title starting with a
    spurious '5. '). This caused two real false-positive 'duplicate
    header' findings on docs/LLMOS_LEDGER_SECURITY_SPEC.md's genuine
    5.5 and 7.5 sub-sections. Not found by an external audit this
    time -- found by actually running the project's own tooling on
    itself during routine housekeeping."""

    def test_decimal_header_parses_as_complete_number_not_truncated(self):
        text = "## 5.5. Telemetry promotion chain\ncontent here\n"
        headers = adl.parse_headers(text)
        self.assertEqual(len(headers), 1)
        self.assertEqual(headers[0]["number"], "5.5")
        self.assertEqual(headers[0]["title"], "Telemetry promotion chain")

    def test_whole_number_header_still_parses_correctly(self):
        text = "## 5. Revocation\ncontent here\n"
        headers = adl.parse_headers(text)
        self.assertEqual(headers[0]["number"], "5")
        self.assertEqual(headers[0]["title"], "Revocation")

    def test_decimal_and_whole_number_not_flagged_as_duplicate(self):
        """The exact real-world case that surfaced this bug: section 5
        and section 5.5 coexisting must not be treated as the same
        header number."""
        text = "## 5. Revocation\ncontent\n## 5.5. Promotion chain\ncontent\n## 6. Retrieval\ncontent\n"
        headers = adl.parse_headers(text)
        snapshot = {"path": "test.md", "headers": headers}
        findings = adl.check_structural(snapshot)
        self.assertEqual(findings, [])

    def test_genuine_duplicate_whole_number_still_detected(self):
        text = "## 1. First\nc\n## 2. Second\nc\n## 2. Actually duplicated\nc\n"
        headers = adl.parse_headers(text)
        snapshot = {"path": "test.md", "headers": headers}
        findings = adl.check_structural(snapshot)
        dup_findings = [f for f in findings if "Duplicate" in f.description]
        self.assertEqual(len(dup_findings), 1)
        self.assertIn("2", dup_findings[0].description)

    def test_genuine_gap_in_whole_numbers_still_detected(self):
        text = "## 1. First\nc\n## 2. Second\nc\n## 5. Skips ahead\nc\n"
        headers = adl.parse_headers(text)
        snapshot = {"path": "test.md", "headers": headers}
        findings = adl.check_structural(snapshot)
        gap_findings = [f for f in findings if "gap" in f.description]
        self.assertEqual(len(gap_findings), 2)  # missing 3 and 4

    def test_decimal_subsections_do_not_trigger_false_gap_findings(self):
        """5.5 existing between 5 and 6 must not be read as 'expected 5.5
        as a whole number and it's missing' or otherwise pollute gap
        analysis, which is restricted to whole integers only."""
        text = "## 5. Revocation\nc\n## 5.5. Promotion chain\nc\n## 6. Retrieval\nc\n"
        headers = adl.parse_headers(text)
        snapshot = {"path": "test.md", "headers": headers}
        findings = adl.check_structural(snapshot)
        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
