# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Tests the claim flagged as a real gap in this project's own audit
trail: session-close has no rollback if a step fails partway through.
This wasn't previously testable in isolation because PROJECT_ROOT in
paths.py had no environment override (unlike every other path
constant) -- every session-close run this session, deliberate or not,
committed to this project's REAL .git history. Fixed alongside this
test (LLMOS_PROJECT_ROOT env var added to paths.py).

Runs session-close as a real subprocess against a disposable temp
directory with its own git repo -- a fresh process is required for the
env-var overrides to take effect cleanly (the constants in paths.py
are read once at import time).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def _git(args, cwd):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, check=True)


class TestSessionClosePartialFailure(unittest.TestCase):
    def setUp(self):
        # Real bug found by an independent ChatGPT audit 2026-08-20,
        # precisely diagnosed: this check used to run WITHOUT cwd
        # override, inheriting the test runner's own working directory
        # (the project root). That let Python find llmos_toolkit via
        # the source tree on sys.path even when the package genuinely
        # ISN'T pip-installed -- passing this check even though the
        # actual test below (which runs with cwd=self.root, a disposable
        # temp dir with no source tree in sight) then fails for real.
        # The check was testing the wrong property: "importable from
        # the project root" instead of "importable the way the real
        # test will actually try it." Confirmed in my own environment
        # this fix is safe -- a genuinely-installed package imports
        # identically with or without the cwd override.
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        # addCleanup, not relying on tearDown -- tearDown doesn't run if
        # setUp raises (including via skipTest below), but addCleanup
        # callbacks do, so the temp dir still gets cleaned up explicitly
        # in the skip case too, not just left for eventual GC.
        self.addCleanup(self.tmp.cleanup)

        check = subprocess.run(
            [sys.executable, "-c", "import llmos_toolkit"],
            capture_output=True, text=True, cwd=str(self.root),
        )
        if check.returncode != 0:
            self.skipTest(
                "llmos_toolkit is not importable from this interpreter "
                f"({sys.executable}) when run outside the source tree "
                "(as the real session-close subprocess call does). Run "
                "`pip install -e .` from the project root in this same "
                "environment before running this test file -- this is "
                "an environment setup gap, not a bug in session-close "
                "itself."
            )
        for d in ("kernel", "projects", "reference", "state", "rag"):
            (self.root / d).mkdir()
        (self.root / "kernel" / "test_kernel.md").write_text("# Test Kernel\nSome content.\n")

        _git(["init", "-q"], self.root)
        _git(["config", "user.email", "test@test.local"], self.root)
        _git(["config", "user.name", "Test"], self.root)
        (self.root / "README.md").write_text("seed\n")
        _git(["add", "-A"], self.root)
        _git(["commit", "-q", "-m", "seed"], self.root)

        self.env = dict(os.environ)
        self.env.update({
            "LLMOS_PROJECT_ROOT": str(self.root),
            "LLMOS_STATE_DIR": str(self.root / "state"),
            "LLMOS_KERNEL_DIR": str(self.root / "kernel"),
            "LLMOS_PROJECTS_DIR": str(self.root / "projects"),
            "LLMOS_DOCS_DIR": str(self.root / "docs"),
            "LLMOS_RAG_DIR": str(self.root / "rag"),
        })

    def _run_session_close(self, extra_args=None):
        cmd = [sys.executable, "-m", "llmos_toolkit", "session-close"] + (extra_args or [])
        return subprocess.run(cmd, cwd=self.root, env=self.env, capture_output=True, text=True, timeout=60)

    def test_full_pipeline_succeeds_in_isolation_and_never_touches_real_project(self):
        real_handoff = Path(__file__).resolve().parent.parent / "rag" / "SESSION_HANDOFF.md"
        real_mtime_before = real_handoff.stat().st_mtime if real_handoff.exists() else None

        result = self._run_session_close()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.root / "rag" / "SESSION_HANDOFF.md").exists())
        self.assertTrue((self.root / "rag" / "handoff_rag.db").exists())

        real_mtime_after = real_handoff.stat().st_mtime if real_handoff.exists() else None
        self.assertEqual(real_mtime_before, real_mtime_after, "isolated run must not touch the real project's rag/ files")

    def test_commit_failure_aborts_before_compaction_runs(self):
        """Characterizes actual current behavior (no rollback spec exists):
        if step 4 (commit) fails, step 5 (compaction) never runs at all,
        even though steps 1-3 already wrote real files to disk. This is
        the gap itself, made visible and pinned down by a test rather
        than left as an unverified assumption."""
        # a stale index.lock reliably makes any git add/commit fail
        (self.root / ".git" / "index.lock").write_text("")

        # seed a ledger with more than the compact threshold so a
        # skipped step 5 is actually detectable, not just a no-op either way
        ledger = self.root / "state" / "growth_ledger.jsonl"
        with open(ledger, "w") as f:
            for i in range(25):
                f.write(json.dumps({"event": "test_entry", "label": f"entry_{i}", "timestamp": "2026-08-14T00:00:00Z"}) + "\n")

        result = self._run_session_close()

        self.assertNotEqual(result.returncode, 0, "a real git failure must propagate as a non-zero exit")
        # steps 1-3 artifacts exist despite the later failure -- no rollback
        self.assertTrue((self.root / "rag" / "handoff_rag.db").exists(), "index step's output should still exist -- no rollback happens")
        self.assertTrue((self.root / "rag" / "SESSION_HANDOFF.md").exists(), "handoff step's output should still exist -- no rollback happens")
        # step 5 never ran: ledger should be untouched (still 25 raw lines, no skeleton)
        lines = ledger.read_text().splitlines()
        self.assertEqual(len(lines), 25, "compaction (step 5) should NOT have run after the step 4 failure")

        (self.root / ".git" / "index.lock").unlink()

    def test_no_commit_flag_skips_commit_but_still_runs_compaction(self):
        ledger = self.root / "state" / "growth_ledger.jsonl"
        with open(ledger, "w") as f:
            for i in range(25):
                f.write(json.dumps({"event": "test_entry", "label": f"entry_{i}", "timestamp": "2026-08-14T00:00:00Z"}) + "\n")

        result = self._run_session_close(["--no-commit"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        lines = ledger.read_text().splitlines()
        self.assertLess(len(lines), 25, "compaction should still run even when commit is explicitly skipped")

    def test_second_commit_failure_now_propagates_nonzero_exit(self):
        """Real bug caught by external audit 2026-08-17: the compaction
        commit's failure was printed but the function fell through to
        return 0 regardless. session-close runs in a real subprocess
        (see _run_session_close), so mocking subprocess.run in THIS
        process has no effect there -- caught that mistake while writing
        this test. Real fix: a git pre-commit hook that allows the first
        commit through but fails every commit after it, via a counter
        file, forcing exactly the second (compaction) commit to fail."""
        ledger = self.root / "state" / "growth_ledger.jsonl"
        with open(ledger, "w") as f:
            for i in range(25):
                f.write(json.dumps({"event": "test_entry", "label": f"entry_{i}", "timestamp": "2026-08-14T00:00:00Z"}) + "\n")

        hooks_dir = self.root / ".git" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        counter_file = self.root / ".git" / "commit_counter"
        counter_file.write_text("0")
        hook_path = hooks_dir / "pre-commit"
        hook_path.write_text(
            "#!/bin/sh\n"
            f'COUNT=$(cat "{counter_file}")\n'
            f'echo $((COUNT + 1)) > "{counter_file}"\n'
            'if [ "$COUNT" -ge "1" ]; then exit 1; fi\n'
            'exit 0\n'
        )
        hook_path.chmod(0o755)

        result = self._run_session_close([])

        hook_path.unlink()
        counter_file.unlink()

        self.assertNotEqual(result.returncode, 0,
                             "second (compaction) commit failure must now propagate a non-zero exit code")
        self.assertIn("Compaction commit failed", result.stdout)


if __name__ == "__main__":
    unittest.main()
