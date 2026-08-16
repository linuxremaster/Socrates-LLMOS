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

    def _log(self, subject, category, severity, description, observer="unspecified", verified=False, source="", subject_version=""):
        args = argparse.Namespace(
            subject=subject, category=category, severity=severity, description=description,
            observer=observer, verified=verified, source=source, subject_version=subject_version,
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
        args = argparse.Namespace(observation_id=obs_id, outcome="confirmed", description="checked, held up", verified=True, amend=False)
        rc = self.plugin.cmd_record_outcome(args)
        self.assertEqual(rc, 0)
        outcomes = self.plugin._load_outcomes()
        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes[0]["observation_id"], obs_id)
        self.assertEqual(outcomes[0]["outcome"], "confirmed")

    def test_record_outcome_rejects_unknown_id(self):
        args = argparse.Namespace(observation_id="nonexistent", outcome="confirmed", description="x", verified=False, amend=False)
        rc = self.plugin.cmd_record_outcome(args)
        self.assertEqual(rc, 1, "an outcome for an id that was never logged must be rejected, not silently written")
        self.assertEqual(len(self.plugin._load_outcomes()), 0)

    def test_summary_calculates_calibration_rate_once_outcomes_exist(self):
        self._log("subj", "cat", "medium", "desc", observer="claude")
        obs_id = self.plugin._load_observations()[0]["observation_id"]
        args = argparse.Namespace(observation_id=obs_id, outcome="confirmed", description="held up", verified=True, amend=False)
        self.plugin.cmd_record_outcome(args)
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("confirmed rate: 1/1", out)

    def test_duplicate_outcome_rejected_without_amend(self):
        self._log("subj", "cat", "medium", "desc")
        obs_id = self.plugin._load_observations()[0]["observation_id"]
        first = argparse.Namespace(observation_id=obs_id, outcome="confirmed", description="d1", verified=True, amend=False)
        second = argparse.Namespace(observation_id=obs_id, outcome="disconfirmed", description="d2", verified=True, amend=False)
        rc1 = self.plugin.cmd_record_outcome(first)
        rc2 = self.plugin.cmd_record_outcome(second)
        self.assertEqual(rc1, 0)
        self.assertEqual(rc2, 1, "a second outcome for the same observation must be rejected without --amend")
        self.assertEqual(len(self.plugin._load_outcomes()), 1)

    def test_amend_allows_correction_and_calibration_uses_only_latest(self):
        self._log("subj", "cat", "medium", "desc", observer="claude")
        obs_id = self.plugin._load_observations()[0]["observation_id"]
        first = argparse.Namespace(observation_id=obs_id, outcome="confirmed", description="wrong initial read", verified=True, amend=False)
        amended = argparse.Namespace(observation_id=obs_id, outcome="disconfirmed", description="corrected after closer check", verified=True, amend=True)
        self.plugin.cmd_record_outcome(first)
        rc = self.plugin.cmd_record_outcome(amended)
        self.assertEqual(rc, 0, "--amend must allow a second outcome for the same id")
        self.assertEqual(len(self.plugin._load_outcomes()), 2, "both entries exist in the ledger (append-only)")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(argparse.Namespace())
        out = buf.getvalue()
        # only the LATEST (disconfirmed) outcome should count -- must not show confirmed rate 1/1
        self.assertNotIn("confirmed rate: 1/1", out, "amended outcome must replace the original for calibration, not add to it")

    def test_calibration_separates_verified_from_asserted_only(self):
        self._log("s1", "c1", "medium", "d1", observer="claude")
        self._log("s2", "c1", "medium", "d2", observer="gemini")
        id1 = [o for o in self.plugin._load_observations() if o["subject"] == "s1"][0]["observation_id"]
        id2 = [o for o in self.plugin._load_observations() if o["subject"] == "s2"][0]["observation_id"]
        self.plugin.cmd_record_outcome(argparse.Namespace(observation_id=id1, outcome="confirmed", description="checked for real", verified=True, amend=False))
        self.plugin.cmd_record_outcome(argparse.Namespace(observation_id=id2, outcome="confirmed", description="just asserted", verified=False, amend=False))
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("1 independently verified, 1 asserted only", out)

    def test_version_drift_no_data_is_honest_not_fabricated(self):
        self._log("subj", "cat", "low", "desc")  # no subject_version given
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_version_drift_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("nothing to compare across versions", out)

    def test_version_drift_single_version_reports_nothing_to_compare(self):
        self._log("subj", "cat", "low", "desc", subject_version="claude-sonnet-5")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_version_drift_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("no cross-version comparison possible yet", out)

    def test_version_drift_two_versions_produces_real_comparison(self):
        self._log("subj1", "shared-cat", "high", "old behavior", subject_version="claude-sonnet-4")
        self._log("subj2", "shared-cat", "low", "new behavior", subject_version="claude-sonnet-5")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_version_drift_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("real cross-version signal", out)
        self.assertIn("claude-sonnet-4", out)
        self.assertIn("claude-sonnet-5", out)


if __name__ == "__main__":
    unittest.main()
