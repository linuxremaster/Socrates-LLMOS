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

from llmos_toolkit.core.paths import PROJECT_ROOT, get_rag_path
from llmos_toolkit.plugins.handoff_rag.plugin import DB_FILE, cmd_handoff, cmd_index


def cmd_session_close(args: argparse.Namespace) -> int:
    print("[1/3] Re-indexing project (kernel, projects, reference)...")
    index_args = argparse.Namespace(dirs=["kernel", "projects", "reference"], db=str(DB_FILE))
    rc = cmd_index(index_args)
    if rc != 0:
        print("  index step failed, stopping.")
        return rc

    print("[2/3] Regenerating handoff pointer doc...")
    handoff_path = get_rag_path("SESSION_HANDOFF.md")
    handoff_args = argparse.Namespace(db=str(DB_FILE), output=str(handoff_path))
    rc = cmd_handoff(handoff_args)
    if rc != 0:
        print("  handoff step failed, stopping.")
        return rc

    if args.no_commit:
        print("[3/3] Skipped commit (--no-commit).")
        return 0

    print("[3/3] Committing via git...")
    git_dir = PROJECT_ROOT / ".git"
    if not git_dir.is_dir():
        print("  No .git repo found here — skipping commit. Run `git init` first, or pass --no-commit to suppress this message.")
        return 0

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

    return 0


def _configure_session_close(p: argparse.ArgumentParser) -> None:
    p.add_argument("--no-commit", action="store_true", help="Re-index and regenerate handoff, but skip the git commit step")
    p.add_argument("--message", help="Custom commit message (default: auto-generated with timestamp)")


def register(registry) -> None:
    registry.register(
        "session-close", cmd_session_close,
        help="Re-index project, regenerate handoff doc, and commit — run this at the end of a working session",
        configure_parser=_configure_session_close, source="session_close",
    )
