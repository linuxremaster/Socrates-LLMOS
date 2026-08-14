# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Confirms tests/ is excluded from secret scanning -- test fixtures
deliberately contain fake-secret-shaped strings, and scanning them
produced real friction (a legitimate FAIL) the first time this harness
was run against the live project. This is the regression guard for
that fix, and also confirms the exclusion doesn't accidentally widen to
exclude real project directories that happen to contain a file with
"test" in the name.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from llmos_toolkit.plugins.secret_scanner.plugin import _is_self


class TestScannerTestsExclusion(unittest.TestCase):
    def test_file_under_tests_dir_is_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests_dir = root / "tests"
            tests_dir.mkdir()
            f = tests_dir / "test_something.py"
            f.write_text("API_KEY = 'sk-fake'\n")
            self.assertTrue(_is_self(f))

    def test_file_named_test_something_outside_tests_dir_is_not_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            f = root / "test_something.py"
            f.write_text("API_KEY = 'sk-fake'\n")
            self.assertFalse(_is_self(f), "a file merely named test_*.py outside a tests/ dir must still be scanned")


if __name__ == "__main__":
    unittest.main()
