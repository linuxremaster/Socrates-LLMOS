# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Tests the claim flagged as UNKNOWN in this project's own audit trail:
git-sync-pull's --ff-only refusal was only ever exercised on a clean
two-clone round trip, never on a genuine diverged-history conflict.
This test creates a real conflict (two clones editing the same line of
the same file, both committed) and checks the refusal actually fires
instead of silently merging or corrupting either clone.

Runs entirely in a disposable tmp directory -- never touches this
project's own .git history.
"""
from __future__ import annotations

import argparse
import subprocess
import tempfile
import unittest
from pathlib import Path

from llmos_toolkit.plugins.git_sync.plugin import cmd_pull, cmd_status


def _git(args, cwd):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, check=True)


class TestGitSyncConflict(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

        # bare "remote" both clones push/pull against
        self.remote = self.root / "remote.git"
        self.remote.mkdir()
        _git(["init", "--bare", "-q"], self.remote)

        self.clone_a = self.root / "clone_a"
        self.clone_b = self.root / "clone_b"
        for clone in (self.clone_a, self.clone_b):
            _git(["clone", "-q", str(self.remote), str(clone)], self.root)
            _git(["config", "user.email", "test@test.local"], clone)
            _git(["config", "user.name", "Test"], clone)

        # seed the remote with a real file both clones will edit
        (self.clone_a / "shared.md").write_text("line one\n")
        _git(["add", "-A"], self.clone_a)
        _git(["commit", "-q", "-m", "seed"], self.clone_a)
        _git(["push", "-q", "origin", "HEAD:master"], self.clone_a)
        _git(["pull", "-q"], self.clone_b)

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_round_trip_still_works(self):
        """Baseline: non-conflicting change should pull cleanly (regression guard for the happy path already manually verified this session)."""
        (self.clone_a / "shared.md").write_text("line one\nline two from A\n")
        _git(["commit", "-aq", "-m", "A edits"], self.clone_a)
        _git(["push", "-q", "origin", "HEAD:master"], self.clone_a)

        rc = cmd_pull(argparse.Namespace(repo=str(self.clone_b)))
        self.assertEqual(rc, 0, "clean pull should succeed")
        self.assertIn("line two from A", (self.clone_b / "shared.md").read_text())

    def test_real_conflict_is_refused_not_silently_merged(self):
        """The actual gap: both clones edit the SAME line and both commit -- diverged history, real conflict."""
        (self.clone_a / "shared.md").write_text("line one EDITED BY A\n")
        _git(["commit", "-aq", "-m", "A edits line one"], self.clone_a)
        _git(["push", "-q", "origin", "HEAD:master"], self.clone_a)

        (self.clone_b / "shared.md").write_text("line one EDITED BY B\n")
        _git(["commit", "-aq", "-m", "B edits line one, diverged"], self.clone_b)

        before = (self.clone_b / "shared.md").read_text()
        rc = cmd_pull(argparse.Namespace(repo=str(self.clone_b)))

        self.assertNotEqual(rc, 0, "a real diverged conflict must be refused, not silently resolved")
        after = (self.clone_b / "shared.md").read_text()
        self.assertEqual(before, after, "clone_b's uncommitted-to-remote work must be untouched after a refused pull")

        # confirm clone_b's own commit is still intact, not lost or rewritten
        code, log_out, _ = subprocess.run(
            ["git", "log", "-1", "--format=%s"], cwd=self.clone_b, capture_output=True, text=True
        ).returncode, subprocess.run(
            ["git", "log", "-1", "--format=%s"], cwd=self.clone_b, capture_output=True, text=True
        ).stdout.strip(), None
        self.assertEqual(log_out, "B edits line one, diverged")

    def test_status_reports_after_refused_pull(self):
        """cmd_status should still work and report something sane after a refused pull -- not crash on divergent state."""
        (self.clone_a / "shared.md").write_text("A change\n")
        _git(["commit", "-aq", "-m", "A"], self.clone_a)
        _git(["push", "-q", "origin", "HEAD:master"], self.clone_a)
        (self.clone_b / "shared.md").write_text("B change\n")
        _git(["commit", "-aq", "-m", "B"], self.clone_b)
        cmd_pull(argparse.Namespace(repo=str(self.clone_b)))

        # should not raise
        rc = cmd_status(argparse.Namespace(repo=str(self.clone_b)))
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
