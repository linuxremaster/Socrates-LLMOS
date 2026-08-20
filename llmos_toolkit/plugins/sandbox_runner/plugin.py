# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Real, honestly-scoped guardrails for running untrusted/experimental
code -- NOT container-grade isolation. Docker, firejail, and bwrap are
not available in this environment (confirmed by direct check, not
assumed), and are unlikely to be available in Termux either, since
Android restricts unprivileged kernel namespace creation more than a
typical Linux host does. Full isolation (a genuine security boundary
against a malicious or buggy process) is not what this provides.

What it actually provides, all real and independently working on any
standard Linux/Termux Python install:
  - CPU time and memory limits via resource.setrlimit -- a runaway
    script gets killed, not left to consume the host indefinitely.
  - A disposable, clearly-separated working directory, wiped between
    runs -- containment by discipline, not by kernel enforcement. A
    sufficiently determined process could still escape via absolute
    paths; this stops accidents and casual missteps, not attacks.
  - No inherited credentials -- the subprocess gets a stripped
    environment (no API keys, no ambient auth), so even code that
    tries to reach the network has nothing to authenticate with. Not
    the same as a real network block, which would need root-level
    firewall/namespace control this environment doesn't have.

Ties into the existing quarantine boundary: a sandboxed run's result
is proposed via propose-observation, never auto-committed to the real
ledger.
"""
from __future__ import annotations

import argparse
import json
import resource
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from llmos_toolkit.core.paths import get_state_path

SANDBOX_DIR_NAME = "sandbox_runs"


def _sandbox_root() -> Path:
    d = get_state_path(SANDBOX_DIR_NAME)
    if not isinstance(d, Path):
        d = Path(d)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _limit_resources(cpu_seconds: int, memory_mb: int):
    """Runs in the child process, right before exec -- sets hard
    resource caps for THIS process only, never affects the parent."""
    def _apply():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        mem_bytes = memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    return _apply


def cmd_sandbox_run(args: argparse.Namespace) -> int:
    """Runs a single Python script under real, working resource limits,
    in a disposable directory, with no inherited credentials. Prints
    the result -- does not auto-log anything; pair with
    propose-observation if the result is worth recording."""
    script_path = Path(args.script)
    if not script_path.is_file():
        print(f"Not a file: {script_path}", file=sys.stderr)
        return 1

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    run_dir = _sandbox_root() / run_id
    run_dir.mkdir(parents=True)
    script_copy = run_dir / script_path.name
    shutil.copy(script_path, script_copy)

    minimal_env = {"PATH": "/usr/bin:/bin", "HOME": str(run_dir)}

    try:
        result = subprocess.run(
            [sys.executable, str(script_copy)],
            cwd=str(run_dir),
            env=minimal_env,
            preexec_fn=_limit_resources(args.cpu_seconds, args.memory_mb),
            capture_output=True,
            text=True,
            timeout=args.cpu_seconds + 5,  # hard outer bound in case the CPU limit signal is missed
        )
        outcome = {
            "run_id": run_id,
            "exit_code": result.returncode,
            "stdout": result.stdout[-4000:],  # capped -- a runaway print loop shouldn't flood this
            "stderr": result.stderr[-4000:],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as e:
        outcome = {
            "run_id": run_id,
            "exit_code": None,
            "stdout": (e.stdout or "")[-4000:] if isinstance(e.stdout, str) else "",
            "stderr": (e.stderr or "")[-4000:] if isinstance(e.stderr, str) else "",
            "timed_out": True,
        }

    (run_dir / "result.json").write_text(json.dumps(outcome, indent=2), encoding="utf-8")
    print(f"Sandbox run {run_id} complete (limits: {args.cpu_seconds}s CPU, {args.memory_mb}MB memory)")
    print(f"  exit_code: {outcome['exit_code']}  timed_out: {outcome['timed_out']}")
    if outcome["stdout"]:
        print(f"  stdout:\n{outcome['stdout']}")
    if outcome["stderr"]:
        print(f"  stderr:\n{outcome['stderr']}")
    print(f"  Full result: {run_dir / 'result.json'}")
    print(f"  Not logged to the real ledger -- use propose-observation if this result is worth recording.")
    return 0


def _configure_sandbox_run(p: argparse.ArgumentParser) -> None:
    p.add_argument("script", help="Path to a Python script to run under sandbox limits")
    p.add_argument("--cpu-seconds", type=int, default=10, help="CPU time limit (default: 10)")
    p.add_argument("--memory-mb", type=int, default=256, help="Memory limit in MB (default: 256)")


def cmd_sandbox_reset(args: argparse.Namespace) -> int:
    """Wipes all sandbox run history clean. Only ever removes
    state/sandbox_runs/ -- never touches the real project."""
    root = _sandbox_root()
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    print(f"Sandbox reset: {root} is now empty.")
    return 0


def cmd_sandbox_list(args: argparse.Namespace) -> int:
    """Lists past sandbox runs, most recent first."""
    root = _sandbox_root()
    runs = sorted([d for d in root.iterdir() if d.is_dir()], reverse=True)
    if not runs:
        print("No sandbox runs yet.")
        return 0
    for d in runs:
        result_file = d / "result.json"
        if result_file.exists():
            r = json.loads(result_file.read_text())
            print(f"{d.name}: exit={r['exit_code']} timed_out={r['timed_out']}")
        else:
            print(f"{d.name}: (no result.json found)")
    return 0


def register(registry) -> None:
    registry.register(
        "sandbox-run", cmd_sandbox_run,
        help="Run a Python script under real CPU/memory limits, in a disposable directory, with no inherited credentials -- NOT full container isolation, see plugin docstring for exact scope",
        configure_parser=_configure_sandbox_run, source="sandbox_runner",
    )
    registry.register(
        "sandbox-reset", cmd_sandbox_reset,
        help="Wipe all sandbox run history clean",
        configure_parser=lambda p: None, source="sandbox_runner",
    )
    registry.register(
        "sandbox-list", cmd_sandbox_list,
        help="List past sandbox runs, most recent first",
        configure_parser=lambda p: None, source="sandbox_runner",
    )
