# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Growth Budget plugin — migrated from the standalone growth_budget.py CLI
into the plugin architecture. Same logic, same ledger format (a checkout
of this ledger from the standalone tool reads fine here and vice versa).
Only the entry point changed: three commands (check, check-dir, log),
registered explicitly via `register(registry)` rather than run as a
top-level script.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

LEDGER_FILE = Path("growth_ledger.jsonl")


def file_stats(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    return {
        "path": str(path),
        "lines": len(lines),
        "chars": len(text),
        "sha256_12": hashlib.sha256(text.encode("utf-8")).hexdigest()[:12],
        "_lines_list": lines,
    }


def diff_summary(old_lines: list, new_lines: list) -> dict:
    sm = difflib.SequenceMatcher(a=old_lines, b=new_lines)
    added = removed = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace":
            removed += i2 - i1
            added += j2 - j1
        elif tag == "delete":
            removed += i2 - i1
        elif tag == "insert":
            added += j2 - j1
    return {"added": added, "removed": removed, "net": added - removed}


def append_ledger(entry: dict) -> None:
    with LEDGER_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def check_one(old_path: Path, new_path: Path, justification, label: str | None = None) -> dict:
    old, new = file_stats(old_path), file_stats(new_path)
    d = diff_summary(old["_lines_list"], new["_lines_list"])
    net = new["lines"] - old["lines"]
    passed = net <= 0 or justification is not None
    return {
        "label": label or new_path.name,
        "old_path": str(old_path), "new_path": str(new_path),
        "old_lines": old["lines"], "new_lines": new["lines"],
        "net_line_delta": net,
        "diff_added": d["added"], "diff_removed": d["removed"],
        "old_sha256_12": old["sha256_12"], "new_sha256_12": new["sha256_12"],
        "justification": justification, "passed": passed,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def print_result(r: dict) -> None:
    status = "PASS" if r["passed"] else "FAIL"
    print(f"[{status}] {r['label']}")
    print(f"  lines: {r['old_lines']} -> {r['new_lines']} (net {r['net_line_delta']:+d})")
    print(f"  diff:  +{r['diff_added']} / -{r['diff_removed']}")
    if r["net_line_delta"] > 0:
        if r["justification"]:
            print(f"  justification (logged): {r['justification']}")
        else:
            print("  REFUSED: net growth with no justification supplied.")
            print('  Pass --justify "<reason>" to log and allow this growth.')


def _configure_check(p: argparse.ArgumentParser) -> None:
    p.add_argument("old")
    p.add_argument("new")
    p.add_argument("--justify", help="Reason for allowing net growth; required if growth > 0")


def cmd_check(args: argparse.Namespace) -> int:
    r = check_one(Path(args.old), Path(args.new), args.justify)
    print_result(r)
    if r["justification"] or r["net_line_delta"] <= 0:
        append_ledger(r)
    return 0 if r["passed"] else 1


def _configure_check_dir(p: argparse.ArgumentParser) -> None:
    p.add_argument("old_dir")
    p.add_argument("new_dir")
    p.add_argument("--justify", help="Reason for allowing net growth across the whole batch")


def cmd_check_dir(args: argparse.Namespace) -> int:
    old_dir, new_dir = Path(args.old_dir), Path(args.new_dir)
    old_files = {p.name: p for p in old_dir.rglob("*") if p.is_file()}
    new_files = {p.name: p for p in new_dir.rglob("*") if p.is_file()}
    common = sorted(set(old_files) & set(new_files))
    added_files = sorted(set(new_files) - set(old_files))
    removed_files = sorted(set(old_files) - set(new_files))

    if not common:
        print("No matching filenames between the two directories -- nothing to compare.")
        return 1

    results, total_old, total_new = [], 0, 0
    for name in common:
        r = check_one(old_files[name], new_files[name], None, label=name)
        results.append(r)
        total_old += r["old_lines"]
        total_new += r["new_lines"]

    for r in results:
        print_result(r)
        print()

    print("=" * 50)
    print(f"TOTAL across {len(common)} matched file(s): {total_old} -> {total_new} lines "
          f"(net {total_new - total_old:+d})")
    if added_files:
        print(f"New files not in old set: {', '.join(added_files)}")
    if removed_files:
        print(f"Files removed from old set: {', '.join(removed_files)}")

    total_net = total_new - total_old
    passed = total_net <= 0 or args.justify is not None

    if passed:
        append_ledger({
            "label": f"batch: {old_dir} -> {new_dir}",
            "files": [r["label"] for r in results],
            "total_old_lines": total_old, "total_new_lines": total_new,
            "net_line_delta": total_net, "justification": args.justify,
            "passed": True, "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        print(f"\n[PASS] Batch total is {'flat/shrinking' if total_net <= 0 else 'justified: ' + args.justify}")
    else:
        print(f"\n[FAIL] Batch grew by {total_net} lines total, no --justify given. Not logged, not passed.")
    return 0 if passed else 1


def _configure_log(p: argparse.ArgumentParser) -> None:
    p.add_argument("-n", type=int, help="Show only the last N entries")


def cmd_log(args: argparse.Namespace) -> int:
    if not LEDGER_FILE.exists():
        print("No ledger yet -- no checks have been logged.")
        return 0
    entries = [json.loads(line) for line in LEDGER_FILE.read_text().splitlines() if line.strip()]
    if args.n:
        entries = entries[-args.n:]
    for e in entries:
        label = e.get("label", "?")
        net = e.get("net_line_delta", e.get("total_new_lines", 0) - e.get("total_old_lines", 0))
        just = e.get("justification")
        ts = e.get("timestamp", "?")
        line = f"{ts}  {label}  net {net:+d}"
        if just:
            line += f"  -- {just}"
        print(line)
    print(f"\n{len(entries)} entries shown.")
    return 0


def register(registry) -> None:
    """Explicit registration API — called by the plugin loader right after import."""
    registry.register("check", cmd_check, help="Compare one old file to one new file",
                       configure_parser=_configure_check, source="growth_budget")
    registry.register("check-dir", cmd_check_dir, help="Compare matching filenames across two directories, summed",
                       configure_parser=_configure_check_dir, source="growth_budget")
    registry.register("log", cmd_log, help="Show the growth ledger",
                       configure_parser=_configure_log, source="growth_budget")
