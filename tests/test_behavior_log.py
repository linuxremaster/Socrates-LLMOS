# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Tests for behavior_log -- previously had no dedicated test file despite
every other feature this session getting one. Caught by external audit,
not self-discovered.
"""
from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class TestBehaviorLog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger_path = Path(self.tmp.name) / "growth_ledger.jsonl"
        self.patcher = mock.patch(
            "llmos_toolkit.plugins.behavior_log.plugin.get_state_path",
            return_value=self.ledger_path,
        )
        self.patcher.start()
        from llmos_toolkit.plugins.behavior_log import plugin
        self.plugin = plugin

    def tearDown(self):
        self.patcher.stop()
        self.tmp.cleanup()

    def _log(self, subject, category, severity, description, observer="unspecified", verified=False, source=""):
        args = argparse.Namespace(
            subject=subject, category=category, severity=severity, description=description,
            observer=observer, verified=verified, source=source,
        )
        return self.plugin.cmd_log_observation(args)

    def test_log_creates_entry_with_expected_fields(self):
        self._log("subj", "cat", "medium", "desc", observer="claude", verified=True, source="http://x")
        entries = self.plugin._load_observations()
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e["subject"], "subj")
        self.assertEqual(e["category"], "cat")
        self.assertEqual(e["severity"], "medium")
        self.assertTrue(e["verified_against_transcript"])
        self.assertEqual(e["source_cited"], "http://x")

    def test_source_defaults_to_none_not_empty_string(self):
        self._log("subj", "cat", "low", "desc")
        entries = self.plugin._load_observations()
        self.assertIsNone(entries[0]["source_cited"])

    def test_summary_reports_verified_vs_unverified_split(self):
        self._log("s1", "c1", "high", "d1", verified=True)
        self._log("s2", "c1", "high", "d2", verified=False)
        args = argparse.Namespace()
        # capture stdout
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(args)
        out = buf.getvalue()
        self.assertIn("1/2", out)

    def test_provenance_diversity_flags_shared_source_as_contamination(self):
        self._log("subj", "cat", "medium", "d1", observer="claude", source="http://same.example")
        self._log("subj", "cat", "medium", "d2", observer="gemini", source="http://same.example")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("likely shared contamination", out)

    def test_provenance_diversity_flags_distinct_sources_as_independent(self):
        self._log("subj", "cat", "medium", "d1", observer="claude", source="http://a.example")
        self._log("subj", "cat", "medium", "d2", observer="gemini", source="http://b.example")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("genuine independence signal", out)

    def test_non_observation_ledger_entries_are_ignored(self):
        # write a non-behavioral_observation entry directly -- must not be counted
        self.ledger_path.write_text(json.dumps({"event": "bug_fix", "label": "unrelated"}) + "\n")
        self._log("subj", "cat", "low", "d1")
        entries = self.plugin._load_observations()
        self.assertEqual(len(entries), 1, "only the behavioral_observation entry should be loaded, not the bug_fix one")

    def test_empty_ledger_summary_does_not_crash(self):
        args = argparse.Namespace()
        rc = self.plugin.cmd_summary(args)
        self.assertEqual(rc, 0)


    def test_record_outcome_links_to_existing_observation(self):
        self._log("subj", "cat", "medium", "desc")
        obs_id = self.plugin._load_observations()[0]["observation_id"]
        args = argparse.Namespace(observation_id=obs_id, outcome="confirmed", description="checked, held up", verified=True)
        rc = self.plugin.cmd_record_outcome(args)
        self.assertEqual(rc, 0)
        outcomes = self.plugin._load_outcomes()
        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes[0]["observation_id"], obs_id)
        self.assertEqual(outcomes[0]["outcome"], "confirmed")

    def test_record_outcome_rejects_unknown_id(self):
        args = argparse.Namespace(observation_id="nonexistent", outcome="confirmed", description="x", verified=False)
        rc = self.plugin.cmd_record_outcome(args)
        self.assertEqual(rc, 1, "an outcome for an id that was never logged must be rejected, not silently written")
        self.assertEqual(len(self.plugin._load_outcomes()), 0)

    def test_summary_calculates_calibration_rate_once_outcomes_exist(self):
        self._log("subj", "cat", "medium", "desc", observer="claude")
        obs_id = self.plugin._load_observations()[0]["observation_id"]
        args = argparse.Namespace(observation_id=obs_id, outcome="confirmed", description="held up", verified=True)
        self.plugin.cmd_record_outcome(args)
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("confirmed rate: 1/1", out)


if __name__ == "__main__":
    unittest.main()
