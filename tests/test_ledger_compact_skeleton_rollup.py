# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Tests the second compaction tier: once skeleton COUNT exceeds
keep_skeletons, old skeletons roll into one meta-skeleton -- the same
hierarchical-rollup pattern applied one level up, so skeleton growth
doesn't become its own unbounded accumulation over a long project life.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from llmos_toolkit.plugins.ledger_compact.plugin import compact_ledger


class TestLedgerCompactSkeletonRollup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "ledger.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, lines):
        self.path.write_text("\n".join(json.dumps(e) for e in lines) + "\n")

    def test_skeleton_count_below_threshold_no_rollup(self):
        skeletons = [
            {"event": "ledger_skeleton_summary", "entries_summarized": 5, "by_event_type": {}, "labels_touched": []}
            for _ in range(3)
        ]
        self._write(skeletons)
        result = compact_ledger(self.path, keep=20, keep_skeletons=10)
        self.assertEqual(result["status"], "no_op")
        entries = [json.loads(l) for l in self.path.read_text().splitlines()]
        self.assertEqual(len(entries), 3, "skeletons below threshold must not be touched")

    def test_skeleton_count_above_threshold_rolls_up_correctly(self):
        skeletons = [
            {"event": "ledger_skeleton_summary", "entries_summarized": 10,
             "by_event_type": {"bug_fix": 2}, "labels_touched": [f"label_{i}"],
             "period_start": f"2026-01-{i+1:02d}T00:00:00Z"}
            for i in range(15)
        ]
        self._write(skeletons)
        result = compact_ledger(self.path, keep=20, keep_skeletons=10)

        self.assertEqual(result["status"], "skeleton_rollup_only")
        self.assertTrue(result["meta_skeleton_created"])
        self.assertEqual(result["skeletons_rolled_up"], 5, "15 skeletons, keep 10 -> roll up the oldest 5")

        entries = [json.loads(l) for l in self.path.read_text().splitlines()]
        meta = [e for e in entries if e["event"] == "ledger_meta_skeleton_summary"]
        plain = [e for e in entries if e["event"] == "ledger_skeleton_summary"]

        self.assertEqual(len(meta), 1)
        self.assertEqual(len(plain), 10, "10 most recent skeletons must remain untouched")
        self.assertEqual(meta[0]["raw_entries_covered"], 50, "5 rolled skeletons x 10 entries each = 50")
        self.assertEqual(meta[0]["by_event_type"]["bug_fix"], 10, "5 x 2 bug_fix each = 10")

    def test_meta_skeleton_itself_is_never_rolled_up_again(self):
        """Two tiers only -- a meta-skeleton is a terminal artifact in this
        version, not itself subject to further rollup."""
        entries = [{"event": "ledger_meta_skeleton_summary", "skeletons_rolled_up": 5, "raw_entries_covered": 50, "by_event_type": {}}]
        entries += [
            {"event": "ledger_skeleton_summary", "entries_summarized": 1, "by_event_type": {}, "labels_touched": []}
            for _ in range(15)
        ]
        self._write(entries)
        compact_ledger(self.path, keep=20, keep_skeletons=10)
        compact_ledger(self.path, keep=20, keep_skeletons=10)  # run twice -- idempotence check

        final = [json.loads(l) for l in self.path.read_text().splitlines()]
        meta_entries = [e for e in final if e["event"] == "ledger_meta_skeleton_summary"]
        self.assertEqual(len(meta_entries), 1, "meta-skeletons must not accumulate or get re-rolled")

    def test_both_tiers_fire_together_produce_correct_math(self):
        skeletons = [
            {"event": "ledger_skeleton_summary", "entries_summarized": 10, "by_event_type": {"x": 1}, "labels_touched": []}
            for _ in range(12)
        ]
        raw = [{"event": "test_entry", "label": f"e{i}", "timestamp": "2026-08-15T00:00:00Z"} for i in range(30)]
        self._write(skeletons + raw)

        result = compact_ledger(self.path, keep=20, keep_skeletons=10)
        self.assertEqual(result["status"], "compacted")
        self.assertTrue(result["meta_skeleton_created"])
        self.assertEqual(result["entries_kept_raw"], 20)

        final = [json.loads(l) for l in self.path.read_text().splitlines()]
        raw_final = [e for e in final if e["event"] == "test_entry"]
        self.assertEqual(len(raw_final), 20)


if __name__ == "__main__":
    unittest.main()
