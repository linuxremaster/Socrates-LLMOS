# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from llmos_toolkit.plugins.sandbox_runner import plugin


class TestSandboxRunner(unittest.TestCase):
    """Every test here confirms a real guardrail actually fires, not
    just that the command runs without error -- e.g. the CPU test
    uses a genuinely infinite loop and checks it was actually killed,
    not a script that happens to finish quickly."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.state_dir = Path(self.tmpdir.name)
        self.patcher = patch.object(plugin, "get_state_path", lambda name: self.state_dir / name)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tmpdir.cleanup()

    def _write_script(self, content: str) -> Path:
        p = Path(self.tmpdir.name) / "script.py"
        p.write_text(content)
        return p

    def test_normal_script_runs_cleanly(self):
        script = self._write_script("print('ok')")
        args = argparse.Namespace(script=str(script), cpu_seconds=5, memory_mb=128)
        plugin.cmd_sandbox_run(args)
        runs = list((self.state_dir / plugin.SANDBOX_DIR_NAME).iterdir())
        self.assertEqual(len(runs), 1)
        import json
        result = json.loads((runs[0] / "result.json").read_text())
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("ok", result["stdout"])

    def test_cpu_limit_genuinely_kills_infinite_loop(self):
        script = self._write_script("x = 0\nwhile True:\n    x += 1\n")
        args = argparse.Namespace(script=str(script), cpu_seconds=1, memory_mb=128)
        plugin.cmd_sandbox_run(args)
        runs = list((self.state_dir / plugin.SANDBOX_DIR_NAME).iterdir())
        import json
        result = json.loads((runs[0] / "result.json").read_text())
        # SIGKILL from the CPU limit -- confirms the loop was actually
        # terminated, not that it happened to finish
        self.assertEqual(result["exit_code"], -9)

    def test_memory_limit_genuinely_raises_memory_error(self):
        script = self._write_script(
            "data = []\n"
            "while True:\n"
            "    data.append(bytearray(10 * 1024 * 1024))\n"
        )
        args = argparse.Namespace(script=str(script), cpu_seconds=5, memory_mb=32)
        plugin.cmd_sandbox_run(args)
        runs = list((self.state_dir / plugin.SANDBOX_DIR_NAME).iterdir())
        import json
        result = json.loads((runs[0] / "result.json").read_text())
        self.assertIn("MemoryError", result["stderr"])

    def test_subprocess_does_not_inherit_real_credentials(self):
        script = self._write_script(
            "import os\n"
            "print('LEAKED' if 'REAL_SECRET' in os.environ else 'CLEAN')\n"
        )
        args = argparse.Namespace(script=str(script), cpu_seconds=5, memory_mb=128)
        import os
        with patch.dict(os.environ, {"REAL_SECRET": "should-not-leak"}):
            plugin.cmd_sandbox_run(args)
        runs = list((self.state_dir / plugin.SANDBOX_DIR_NAME).iterdir())
        import json
        result = json.loads((runs[0] / "result.json").read_text())
        self.assertIn("CLEAN", result["stdout"])
        self.assertNotIn("LEAKED", result["stdout"])

    def test_reset_genuinely_empties_sandbox_dir(self):
        script = self._write_script("print('run before reset')")
        args = argparse.Namespace(script=str(script), cpu_seconds=5, memory_mb=128)
        plugin.cmd_sandbox_run(args)
        self.assertTrue(any((self.state_dir / plugin.SANDBOX_DIR_NAME).iterdir()))
        plugin.cmd_sandbox_reset(argparse.Namespace())
        self.assertFalse(any((self.state_dir / plugin.SANDBOX_DIR_NAME).iterdir()))


if __name__ == "__main__":
    unittest.main()
