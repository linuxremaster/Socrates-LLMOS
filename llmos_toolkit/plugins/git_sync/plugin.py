# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Git Sync plugin — fills the `sync` plugin's empty slot with a real
backend: plain `git` commands, invoked one at a time, by you or a
session, exactly like every other command in this toolkit.

DESIGN RULE, stated explicitly so a future addition can't violate it by
accident: NOT LIVE, NOT PERSISTENT. This plugin never runs a daemon,
watcher, webhook listener, or background process. Every command here
does exactly one thing (pull, push, or report status) and exits. There
is no mechanism by which a change on GitHub causes anything to happen
here without a command being explicitly run — no event triggers, no
"react when a PR opens." This matches Claude's own actual product
limits (no event-driven GitHub actions, conversation-only, closing the
chat stops everything) and, more importantly, matches this project's
existing multi-instance coordination model: async pull/push through
shared storage, human or session as the transport layer, same as the
Google-Drive-based relay this replaces. If someone later wants a
watcher/webhook/CI-triggered version of this, that is a different,
bigger project with a different risk profile (untrusted automatic
triggers acting on repo content) — it should not quietly grow out of
this plugin's scope.

Uses the `git` CLI via subprocess, not a Python git library — one fewer
dependency, and `git` itself is already assumed available (same
assumption the toolkit's own git pre-commit hook makes).
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def _run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=60,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _configure_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--repo", default=".", help="Path to the git repo (default: current directory)")


def cmd_status(args: argparse.Namespace) -> int:
    repo = Path(args.repo)
    if not (repo / ".git").is_dir():
        print(f"Not a git repo: {repo.resolve()}")
        print("Run `git init` (and set a remote) here first, or point --repo elsewhere.")
        return 1

    code, out, err = _run_git(["status", "--short", "--branch"], repo)
    if code != 0:
        print(f"git status failed: {err}")
        return 1
    print(out or "(clean, nothing pending)")

    code, out, err = _run_git(["log", "-1", "--format=%H %ci %s"], repo)
    if code == 0 and out:
        print(f"\nLast commit: {out}")
    return 0


def cmd_pull(args: argparse.Namespace) -> int:
    repo = Path(args.repo)
    if not (repo / ".git").is_dir():
        print(f"Not a git repo: {repo.resolve()}")
        return 1

    code, out, err = _run_git(["pull", "--ff-only"], repo)
    print(out)
    if code != 0:
        print(f"Pull failed or diverged: {err}")
        print("--ff-only refuses to auto-merge — resolve manually if there's a real conflict.")
        return 1
    return 0


def _configure_push(p: argparse.ArgumentParser) -> None:
    _configure_common(p)
    p.add_argument("--message", "-m", required=True, help="Commit message")
    p.add_argument("--paths", nargs="*", default=["."], help="Paths to add (default: everything)")


def cmd_push(args: argparse.Namespace) -> int:
    repo = Path(args.repo)
    if not (repo / ".git").is_dir():
        print(f"Not a git repo: {repo.resolve()}")
        return 1

    code, out, err = _run_git(["add"] + args.paths, repo)
    if code != 0:
        print(f"git add failed: {err}")
        return 1

    code, out, err = _run_git(["diff", "--cached", "--quiet"], repo)
    if code == 0:
        print("Nothing staged to commit — working tree matches last commit.")
        return 0

    code, out, err = _run_git(["commit", "-m", args.message], repo)
    print(out)
    if code != 0:
        print(f"Commit failed: {err}")
        return 1

    code, out, err = _run_git(["push"], repo)
    print(out)
    if code != 0:
        print(f"Push failed: {err}")
        print("Commit succeeded locally — nothing is lost, just not on the remote yet.")
        return 1
    return 0


def register(registry) -> None:
    registry.register("git-sync-status", cmd_status,
                       help="Show pending changes and last commit — one-shot, no background watching",
                       configure_parser=_configure_common, source="git_sync")
    registry.register("git-sync-pull", cmd_pull,
                       help="Pull latest (fast-forward only) — run this, don't wait for it to happen",
                       configure_parser=_configure_common, source="git_sync")
    registry.register("git-sync-push", cmd_push,
                       help="Add, commit, and push — explicit message required, one-shot",
                       configure_parser=_configure_push, source="git_sync")
