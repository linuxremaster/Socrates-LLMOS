# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Ledger Compact plugin — flushes old raw entries from a jsonl ledger
(growth_ledger.jsonl, drift_audit.jsonl, token_ledger.jsonl) into a
single permanent skeleton summary, keeping only the most recent N raw
entries in full detail.

A skeleton summary entry (event: "ledger_skeleton_summary") is never
itself re-summarized on a later compaction — it's the permanent,
flushed record. Only non-skeleton raw entries beyond the keep window
get rolled up. This mirrors the same rotate-don't-archive pattern used
elsewhere in this project for recurring logs: keep the recent entries
in full, roll older ones into a short dated summary, in batches.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

SKELETON_EVENT = "ledger_skeleton_summary"


def _load_lines(path: Path) -> list[dict]:
    if not path.exists():
        return []
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        lines.append(json.loads(raw))
    return lines


def compact_ledger(path: Path, keep: int) -> dict:
    entries = _load_lines(path)
    skeletons = [e for e in entries if e.get("event") == SKELETON_EVENT]
    raw = [e for e in entries if e.get("event") != SKELETON_EVENT]

    if len(raw) <= keep:
        return {"status": "no_op", "reason": f"{len(raw)} raw entries <= keep threshold {keep}", "total_entries": len(entries)}

    to_summarize = raw[:-keep]
    to_keep_raw = raw[-keep:]

    timestamps = [e.get("timestamp") for e in to_summarize if e.get("timestamp")]
    event_counts = Counter(e.get("event", "unlabeled") for e in to_summarize)
    labels = sorted({e.get("label") for e in to_summarize if e.get("label")})

    skeleton = {
        "event": SKELETON_EVENT,
        "period_start": min(timestamps) if timestamps else None,
        "period_end": max(timestamps) if timestamps else None,
        "entries_summarized": len(to_summarize),
        "by_event_type": dict(event_counts),
        "labels_touched": labels,
        "compacted_at": datetime.now(timezone.utc).isoformat(),
    }

    new_content = skeletons + [skeleton] + to_keep_raw
    path.write_text("\n".join(json.dumps(e) for e in new_content) + "\n", encoding="utf-8")

    return {
        "status": "compacted",
        "entries_summarized": len(to_summarize),
        "entries_kept_raw": len(to_keep_raw),
        "skeleton_summaries_total": len(skeletons) + 1,
        "total_entries_now": len(new_content),
    }


def cmd_compact(args: argparse.Namespace) -> int:
    path = Path(args.file)
    result = compact_ledger(path, args.keep)
    if result["status"] == "no_op":
        print(f"No compaction needed: {result['reason']}")
        return 0
    print(
        f"Compacted {path}: {result['entries_summarized']} old entries -> 1 skeleton summary, "
        f"{result['entries_kept_raw']} recent raw entries kept, "
        f"{result['skeleton_summaries_total']} skeleton summaries total, "
        f"{result['total_entries_now']} lines in file now."
    )
    return 0


def _configure_compact(p: argparse.ArgumentParser) -> None:
    p.add_argument("file", help="Path to the jsonl ledger file to compact")
    p.add_argument("--keep", type=int, default=20, help="Number of most recent raw entries to keep in full (default: 20)")


def register(registry) -> None:
    registry.register(
        "ledger-compact", cmd_compact,
        help="Roll old ledger entries into a permanent skeleton summary, keep recent entries in full",
        configure_parser=_configure_compact, source="ledger_compact",
    )
