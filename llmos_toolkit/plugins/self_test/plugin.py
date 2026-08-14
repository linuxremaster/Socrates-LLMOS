# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Self Test plugin — runs the tests/ harness (unittest, standard library
only, no external test-runner dependency needed). Every test in that
directory runs in a disposable tmp directory or subprocess with
env-var path overrides; none of them touch this project's real state/,
rag/, or .git. See tests/*.py docstrings for what each one actually
verifies and why.
"""
from __future__ import annotations

import argparse
import subprocess
import sys

from llmos_toolkit.core.paths import PROJECT_ROOT


def cmd_self_test(args: argparse.Namespace) -> int:
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
    if args.verbose:
        cmd.append("-v")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode


def _configure_self_test(p: argparse.ArgumentParser) -> None:
    p.add_argument("--verbose", "-v", action="store_true", help="Show each test name and its docstring as it runs")


def register(registry) -> None:
    registry.register(
        "self-test", cmd_self_test,
        help="Run the disposable-harness test suite (tests/) -- isolated, never touches real project state",
        configure_parser=_configure_self_test, source="self_test",
    )
