# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from llmos_toolkit.core import cli as core_cli
from llmos_toolkit.plugins.audit_all import plugin as audit_plugin


class TestKernelPinCollision(unittest.TestCase):
    """Real bug caught by external audit 2026-08-17: pin identity used
    to be path.name (basename only), so two different files sharing a
    filename would collide in the same pin namespace, and the stored
    path field was never actually checked during verification."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.pins_path = Path(self.tmpdir.name) / "kernel_pins.json"
        self.patcher = patch.object(core_cli, "KERNEL_PIN_FILE", self.pins_path)
        self.patcher.start()
        self.patcher2 = patch.object(audit_plugin, "get_state_path", lambda name: self.pins_path)
        self.patcher2.start()

        self.dir1 = Path(self.tmpdir.name) / "dir1"
        self.dir2 = Path(self.tmpdir.name) / "dir2"
        self.dir1.mkdir()
        self.dir2.mkdir()
        (self.dir1 / "policy.md").write_text("content A")
        (self.dir2 / "policy.md").write_text("totally different content B")

    def tearDown(self):
        self.patcher.stop()
        self.patcher2.stop()
        self.tmpdir.cleanup()

    def test_same_basename_different_directories_do_not_collide(self):
        core_cli.cmd_pin_kernel(argparse.Namespace(kernel_file=str(self.dir1 / "policy.md"), label=None))
        core_cli.cmd_pin_kernel(argparse.Namespace(kernel_file=str(self.dir2 / "policy.md"), label=None))
        pins = json.loads(self.pins_path.read_text())
        self.assertEqual(len(pins), 2, "two files sharing a basename must get distinct pin entries, not overwrite each other")

    def test_verification_checks_correct_file_not_wrong_same_name_file(self):
        core_cli.cmd_pin_kernel(argparse.Namespace(kernel_file=str(self.dir1 / "policy.md"), label=None))
        result = audit_plugin._check_kernel_integrity(self.dir1 / "policy.md")
        self.assertEqual(result["status"], "PASS")
        # dir2's policy.md was never pinned -- must fail, not accidentally
        # match dir1's pin just because the filename is the same
        result2 = audit_plugin._check_kernel_integrity(self.dir2 / "policy.md")
        self.assertEqual(result2["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
