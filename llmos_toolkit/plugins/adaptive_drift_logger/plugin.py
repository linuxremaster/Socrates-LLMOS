# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Adaptive Drift Logger plugin — thin wrapper around the standalone
adaptive_drift_logger.py, which stays canonical and independently
runnable exactly as its own README documents:

    python adaptive_drift_logger.py path/to/kernel.md

This wrapper imports that same file by path rather than reimplementing
its logic, so there is exactly one copy of the drift-detection code —
duplicating it here would itself be the kind of drift this whole project
is about avoiding. Registers three commands: drift-log, drift-log-signatures,
drift-log-confirm.

Naming note: this is deliberately distinct from drift-check/drift-add-rule
(the drift_check plugin). That one is a simple requirements.json-style
"has this exact known-bad phrase reappeared" checker. This one is the
five-class, baseline-comparing, self-adaptive checker (growth, semantic,
cross-artifact, embedded-vs-standalone, structural). They're
complementary, not redundant — see each plugin's own docstring.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_IMPL_PATH = Path(__file__).resolve().parent.parent.parent / "adaptive_drift_logger.py"
_spec = importlib.util.spec_from_file_location("adaptive_drift_logger_impl", _IMPL_PATH)
adl = importlib.util.module_from_spec(_spec)
sys.modules["adaptive_drift_logger_impl"] = adl  # required before exec_module — @dataclass looks itself up here
_spec.loader.exec_module(adl)


def _configure_log(p: argparse.ArgumentParser) -> None:
    p.add_argument("artifacts", nargs="+", help="Markdown files to check")
    p.add_argument("--rebaseline", action="store_true", help="Reset baseline to current content")


def cmd_log(args: argparse.Namespace) -> int:
    return adl.cmd_run(args.artifacts, args.rebaseline)


def cmd_signatures(_args: argparse.Namespace) -> int:
    return adl.cmd_list_signatures()


def _configure_confirm(p: argparse.ArgumentParser) -> None:
    p.add_argument("signature_id")
    p.add_argument("--as", dest="as_status", required=True, choices=["real", "false_positive"])


def cmd_confirm(args: argparse.Namespace) -> int:
    return adl.cmd_confirm(args.signature_id, args.as_status)


def register(registry) -> None:
    registry.register("drift-log", cmd_log,
                       help="Five-class adaptive drift check (growth/semantic/cross-artifact/embedded/structural)",
                       configure_parser=_configure_log, source="adaptive_drift_logger")
    registry.register("drift-log-signatures", cmd_signatures,
                       help="List tracked drift-log finding signatures and their confirm status",
                       source="adaptive_drift_logger")
    registry.register("drift-log-confirm", cmd_confirm,
                       help="Confirm a drift-log signature as real or false_positive",
                       configure_parser=_configure_confirm, source="adaptive_drift_logger")
