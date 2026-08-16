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
META_SKELETON_EVENT = "ledger_meta_skeleton_summary"


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


def _rollup_skeletons(skeletons: list[dict], keep_skeletons: int) -> tuple[list[dict], dict | None]:
    """Second tier: once skeleton COUNT itself passes keep_skeletons, roll
    the oldest ones into one meta-skeleton -- same hierarchical-rollup
    pattern as the raw-entry compaction, one level up. If a meta-skeleton
    already exists, MERGE into it rather than creating a second one --
    otherwise meta-skeletons would themselves accumulate unboundedly over
    a long project life, exactly the problem this tier exists to prevent.
    Meta-skeletons are never further rolled up beyond this merge -- two
    tiers is enough for this project's actual scale; a third tier would
    be premature."""
    existing_meta = [s for s in skeletons if s.get("event") == META_SKELETON_EVENT]
    plain = [s for s in skeletons if s.get("event") != META_SKELETON_EVENT]

    if len(plain) <= keep_skeletons:
        return skeletons, None

    to_roll = plain[:-keep_skeletons]
    to_keep = plain[-keep_skeletons:]

    entries_covered = sum(s.get("entries_summarized", 0) for s in to_roll)
    periods = [s.get("period_start") for s in to_roll if s.get("period_start")]
    new_labels = {lbl for s in to_roll for lbl in s.get("labels_touched", [])}
    combined_types = Counter()
    for s in to_roll:
        combined_types.update(s.get("by_event_type", {}))

    if existing_meta:
        # merge into the single existing meta-skeleton instead of appending a second
        prior = existing_meta[0]
        entries_covered += prior.get("raw_entries_covered", 0)
        prior_periods = [prior.get("earliest_period_start")] if prior.get("earliest_period_start") else []
        periods = periods + prior_periods
        combined_types.update(prior.get("by_event_type", {}))
        merged_labels = set(prior.get("labels_touched_sample", [])) | new_labels
        meta_skeleton = {
            "event": META_SKELETON_EVENT,
            "skeletons_rolled_up": prior.get("skeletons_rolled_up", 0) + len(to_roll),
            "raw_entries_covered": entries_covered,
            "earliest_period_start": min(periods) if periods else None,
            "by_event_type": dict(combined_types),
            "labels_touched_sample": sorted(merged_labels)[:30],
            "rolled_up_at": datetime.now(timezone.utc).isoformat(),
        }
        return [meta_skeleton] + to_keep, meta_skeleton

    meta_skeleton = {
        "event": META_SKELETON_EVENT,
        "skeletons_rolled_up": len(to_roll),
        "raw_entries_covered": entries_covered,
        "earliest_period_start": min(periods) if periods else None,
        "by_event_type": dict(combined_types),
        "labels_touched_sample": sorted(new_labels)[:30],
        "rolled_up_at": datetime.now(timezone.utc).isoformat(),
    }
    return [meta_skeleton] + to_keep, meta_skeleton


def compact_ledger(path: Path, keep: int, keep_skeletons: int = 10) -> dict:
    entries = _load_lines(path)
    skeletons = [e for e in entries if e.get("event") in (SKELETON_EVENT, META_SKELETON_EVENT)]
    raw = [e for e in entries if e.get("event") not in (SKELETON_EVENT, META_SKELETON_EVENT)]

    skeletons, meta_result = _rollup_skeletons(skeletons, keep_skeletons)

    if len(raw) <= keep:
        if meta_result is None:
            return {"status": "no_op", "reason": f"{len(raw)} raw entries <= keep threshold {keep}", "total_entries": len(entries)}
        # only the skeleton rollup happened -- still write the file
        path.write_text("\n".join(json.dumps(e) for e in skeletons + raw) + "\n", encoding="utf-8")
        return {
            "status": "skeleton_rollup_only",
            "meta_skeleton_created": True,
            "skeletons_rolled_up": meta_result["skeletons_rolled_up"],
            "total_entries": len(skeletons) + len(raw),
        }

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
        "skeleton_summaries_total": len([s for s in skeletons if s.get("event") == SKELETON_EVENT]) + 1,
        "meta_skeleton_created": meta_result is not None,
        "total_entries_now": len(new_content),
    }


def cmd_compact(args: argparse.Namespace) -> int:
    path = Path(args.file)
    result = compact_ledger(path, args.keep, args.keep_skeletons)
    if result["status"] == "no_op":
        print(f"No compaction needed: {result['reason']}")
        return 0
    if result["status"] == "skeleton_rollup_only":
        print(f"Raw entries below threshold, but rolled up {result['skeletons_rolled_up']} old skeletons into 1 meta-skeleton.")
        return 0
    meta_note = " (also rolled old skeletons into a meta-skeleton)" if result.get("meta_skeleton_created") else ""
    print(
        f"Compacted {path}: {result['entries_summarized']} old entries -> 1 skeleton summary, "
        f"{result['entries_kept_raw']} recent raw entries kept, "
        f"{result['skeleton_summaries_total']} skeleton summaries total, "
        f"{result['total_entries_now']} lines in file now{meta_note}."
    )
    return 0


def _configure_compact(p: argparse.ArgumentParser) -> None:
    p.add_argument("file", help="Path to the jsonl ledger file to compact")
    p.add_argument("--keep", type=int, default=20, help="Number of most recent raw entries to keep in full (default: 20)")
    p.add_argument("--keep-skeletons", type=int, default=10, help="Number of most recent skeleton summaries to keep before rolling old ones into a meta-skeleton (default: 10)")


def register(registry) -> None:
    registry.register(
        "ledger-compact", cmd_compact,
        help="Roll old ledger entries into a permanent skeleton summary, keep recent entries in full",
        configure_parser=_configure_compact, source="ledger_compact",
    )
