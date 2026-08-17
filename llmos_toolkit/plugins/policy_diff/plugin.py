# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Policy Diff plugin -- session-triggered snapshot/compare tool for
provider policy text. NOT autonomous detection: nothing here fetches
anything on its own. The actual fetch step happens in a live
conversation (a real web_fetch against the provider's page); this
tool's job is storing what was fetched and diffing it against what was
stored last time, so a change shows up as an actual text diff instead
of just "something might be different since date X" (that coarser
signal is audit_all's staleness check, a different, complementary
tool).

Workflow: fetch current policy text -> save-policy-snapshot (first
time, or to establish a new baseline) -> next time, fetch again ->
diff-policy-snapshot shows exactly what changed, if anything.
"""
from __future__ import annotations

import argparse
import difflib
import re
from datetime import datetime, timezone
from pathlib import Path

from llmos_toolkit.core.paths import get_state_path


def _sanitize_name(name: str) -> str:
    """Real path-traversal risk if used raw: a name like '../../x' would
    escape the snapshot directory. Only allow a simple identifier."""
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "-", name)
    if not re.search(r"[a-zA-Z0-9]", cleaned):
        raise ValueError("snapshot name must contain at least one alphanumeric character")
    return cleaned


def _snapshot_dir() -> Path:
    d = get_state_path("policy_snapshots")
    d.mkdir(parents=True, exist_ok=True)
    return d


def cmd_save_snapshot(args: argparse.Namespace) -> int:
    safe_name = _sanitize_name(args.name)
    text = Path(args.text_file).read_text(encoding="utf-8")
    snap_dir = _snapshot_dir()
    # Full timestamp, not date-only -- two saves on the same day would
    # otherwise silently overwrite each other, losing temporal provenance
    # for something an evidence/audit tool should never lose.
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%f")
    out_path = snap_dir / f"{safe_name}_{timestamp}.txt"
    out_path.write_text(text, encoding="utf-8")
    print(f"Saved snapshot: {out_path.name} ({len(text)} chars)")
    return 0


def _latest_snapshot(name: str) -> Path | None:
    snap_dir = _snapshot_dir()
    matches = sorted(snap_dir.glob(f"{name}_*.txt"))
    return matches[-1] if matches else None


def cmd_diff_snapshot(args: argparse.Namespace) -> int:
    previous = _latest_snapshot(_sanitize_name(args.name))
    if previous is None:
        print(f"No prior snapshot found for '{args.name}' -- nothing to diff against. "
              f"Use save-policy-snapshot first to establish a baseline.")
        return 1

    new_text = Path(args.text_file).read_text(encoding="utf-8")
    old_text = previous.read_text(encoding="utf-8")

    if new_text == old_text:
        print(f"No change since {previous.name} -- text is byte-identical.")
        return 0

    diff = list(difflib.unified_diff(
        old_text.splitlines(), new_text.splitlines(),
        fromfile=previous.name, tofile="(current fetch)", lineterm="",
    ))
    print(f"CHANGE DETECTED since {previous.name}:\n")
    for line in diff:
        print(line)
    print(f"\n{len(diff)} diff line(s). If this is a real, confirmed change, run "
          f"save-policy-snapshot to establish the new baseline, and consider "
          f"llmos log-boundary-update to record it in EXECUTION_BOUNDARY_UPDATES.md.")
    return 0


def _configure_save(p: argparse.ArgumentParser) -> None:
    p.add_argument("name", help="Short identifier for what this snapshot is (e.g. anthropic-usage-policy)")
    p.add_argument("text_file", help="Path to a file containing the fetched policy text")


def _configure_diff(p: argparse.ArgumentParser) -> None:
    p.add_argument("name", help="Same identifier used when the snapshot was saved")
    p.add_argument("text_file", help="Path to a file containing freshly fetched text to compare")


def register(registry) -> None:
    registry.register(
        "save-policy-snapshot", cmd_save_snapshot,
        help="Save a dated snapshot of fetched provider policy text -- establishes or updates a baseline",
        configure_parser=_configure_save, source="policy_diff",
    )
    registry.register(
        "diff-policy-snapshot", cmd_diff_snapshot,
        help="Diff freshly fetched policy text against the last saved snapshot -- shows what actually changed, not just how long since checked",
        configure_parser=_configure_diff, source="policy_diff",
    )
