# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from llmos_toolkit.plugins.policy_diff import plugin


class TestPolicyDiffSecurity(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.snap_dir = Path(self.tmpdir.name) / "policy_snapshots"
        self.patcher = patch.object(plugin, "get_state_path", lambda name: self.snap_dir)
        self.patcher.start()
        self.text_file = Path(self.tmpdir.name) / "text.txt"
        self.text_file.write_text("some policy text")

    def tearDown(self):
        self.patcher.stop()
        self.tmpdir.cleanup()

    def test_path_traversal_name_is_neutered_not_escaped(self):
        args = argparse.Namespace(name="../../../etc/malicious", text_file=str(self.text_file))
        plugin.cmd_save_snapshot(args)
        # Nothing should have been written outside the snapshot dir
        escaped = Path(self.tmpdir.name) / "etc" / "malicious"
        self.assertFalse(escaped.exists())
        # Something safe should exist inside the snapshot dir instead
        self.assertTrue(any(self.snap_dir.glob("*.txt")))

    def test_empty_or_fully_stripped_name_is_rejected(self):
        args = argparse.Namespace(name="../../..", text_file=str(self.text_file))
        with self.assertRaises(ValueError):
            plugin.cmd_save_snapshot(args)

    def test_same_day_snapshots_do_not_collide(self):
        args1 = argparse.Namespace(name="test-policy", text_file=str(self.text_file))
        plugin.cmd_save_snapshot(args1)
        self.text_file.write_text("changed policy text")
        args2 = argparse.Namespace(name="test-policy", text_file=str(self.text_file))
        plugin.cmd_save_snapshot(args2)
        saved = list(self.snap_dir.glob("test-policy_*.txt"))
        # Both writes must produce distinct files (timestamp precision,
        # not date-only), not one overwriting the other
        self.assertEqual(len(saved), 2, saved)


if __name__ == "__main__":
    unittest.main()
