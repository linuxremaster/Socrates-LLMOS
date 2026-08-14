# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Session Close plugin — closes the staleness gap named in this project's
own handoff doc: rag-index and rag-handoff only reflect whatever was
last indexed, and nothing previously forced a re-index at session end.

This is deliberately thin: it calls the existing handoff_rag commands
(cmd_index, cmd_handoff) rather than reimplementing them, then commits
via git_sync if a repo is present. Does not invent new state — every
artifact it produces already existed as a separate manual step.
"""
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from llmos_toolkit.core.paths import KERNEL_DIR, PROJECT_ROOT, get_rag_path, get_state_path
from llmos_toolkit.plugins.handoff_rag.plugin import DB_FILE, cmd_handoff, cmd_index
from llmos_toolkit.plugins.ledger_compact.plugin import compact_ledger

try:
    from llmos_toolkit.plugins.adaptive_drift_logger.plugin import adl
except ImportError:
    adl = None


def cmd_session_close(args: argparse.Namespace) -> int:
    print("[1/5] Re-indexing project (kernel, projects, reference)...")
    index_args = argparse.Namespace(dirs=["kernel", "projects", "reference"], db=str(DB_FILE))
    rc = cmd_index(index_args)
    if rc != 0:
        print("  index step failed, stopping.")
        return rc

    print("[2/5] Regenerating handoff pointer doc...")
    handoff_path = get_rag_path("SESSION_HANDOFF.md")
    handoff_args = argparse.Namespace(db=str(DB_FILE), output=str(handoff_path))
    rc = cmd_handoff(handoff_args)
    if rc != 0:
        print("  handoff step failed, stopping.")
        return rc

    print("[3/5] Running drift-log against all kernel files...")
    if adl is None:
        print("  adaptive_drift_logger unavailable — skipping this step.")
    else:
        kernel_files = [str(p) for p in sorted(KERNEL_DIR.glob("*.md"))]
        if kernel_files:
            adl.cmd_run(kernel_files, rebaseline=False)
        else:
            print("  No kernel .md files found — skipping.")

    if args.no_commit:
        print("[4/5] Skipped commit (--no-commit).")
    else:
        print("[4/5] Committing via git...")
        git_dir = PROJECT_ROOT / ".git"
        if not git_dir.is_dir():
            print("  No .git repo found here — skipping commit. Run `git init` first, or pass --no-commit to suppress this message.")
        else:
            msg = args.message or f"Session close: re-index + handoff regen ({datetime.now(timezone.utc).isoformat()})"
            try:
                subprocess.run(["git", "-C", str(PROJECT_ROOT), "add", "-A"], check=True, capture_output=True)
                result = subprocess.run(
                    ["git", "-C", str(PROJECT_ROOT), "commit", "-m", msg],
                    capture_output=True, text=True,
                )
                if result.returncode == 0:
                    print(f"  Committed: {msg}")
                elif "nothing to commit" in result.stdout:
                    print("  Nothing changed since last commit.")
                else:
                    print(f"  git commit failed: {result.stderr.strip()}")
                    return 1
            except subprocess.CalledProcessError as e:
                print(f"  git add failed: {e}")
                return 1

    if args.no_compact:
        print("[5/5] Skipped ledger compaction (--no-compact).")
        return 0

    print("[5/5] Compacting ledgers (keep last %d raw entries each)..." % args.compact_keep)
    for ledger_name in ("growth_ledger.jsonl", "drift_audit.jsonl", "token_ledger.jsonl"):
        ledger_path = get_state_path(ledger_name)
        if not ledger_path.exists():
            continue
        result = compact_ledger(ledger_path, args.compact_keep)
        if result["status"] == "no_op":
            print(f"  {ledger_name}: {result['reason']}")
        else:
            print(f"  {ledger_name}: {result['entries_summarized']} entries -> 1 skeleton, {result['entries_kept_raw']} kept raw")

    if not args.no_commit and (PROJECT_ROOT / ".git").is_dir():
        try:
            subprocess.run(["git", "-C", str(PROJECT_ROOT), "add", "-A"], check=True, capture_output=True)
            result = subprocess.run(
                ["git", "-C", str(PROJECT_ROOT), "commit", "-m", "Session close: ledger compaction"],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print("  Compaction committed separately.")
        except subprocess.CalledProcessError:
            pass

    return 0


def _configure_session_close(p: argparse.ArgumentParser) -> None:
    p.add_argument("--no-commit", action="store_true", help="Re-index, handoff, drift-log, and compact, but skip the git commit step")
    p.add_argument("--message", help="Custom commit message (default: auto-generated with timestamp)")
    p.add_argument("--no-compact", action="store_true", help="Skip automatic ledger compaction (step 5). Ledger-compact remains available as its own manual command.")
    p.add_argument("--compact-keep", type=int, default=20, help="Recent raw entries to keep per ledger during automatic compaction (default: 20)")


def register(registry) -> None:
    registry.register(
        "session-close", cmd_session_close,
        help="Re-index project, regenerate handoff doc, and commit — run this at the end of a working session",
        configure_parser=_configure_session_close, source="session_close",
    )
