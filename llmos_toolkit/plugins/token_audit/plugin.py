# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Token Audit plugin — logs an ESTIMATED token count per session/file to a
running ledger, so usage across many accounts/providers is visible in
one place instead of scattered across 15 separate UIs that don't talk to
each other.

Honest limit: the estimate is chars/4, a widely-used rough heuristic —
NOT the actual tokenizer output for Claude, GPT, or Gemini, which all
differ from each other and from this estimate. Treat the numbers as
"roughly comparable across sessions," not "exact." If exact counts
matter for a specific provider, use that provider's own tokenizer.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from llmos_toolkit.core.paths import get_state_path

LEDGER_FILE = get_state_path("token_ledger.jsonl")
CHARS_PER_TOKEN_ESTIMATE = 4


def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / CHARS_PER_TOKEN_ESTIMATE))


def _configure_audit(p: argparse.ArgumentParser) -> None:
    p.add_argument("path", help="A text file, or a directory to sum across all files in it")
    p.add_argument("--label", help="Session/project label (default: filename or dir name)")
    p.add_argument("--rate-per-1k", type=float, help="Optional cost estimate, e.g. 3.00 for $3/1k tokens")


def cmd_audit(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if path.is_dir():
        files = sorted(p for p in path.rglob("*") if p.is_file())
    elif path.is_file():
        files = [path]
    else:
        print(f"Not found: {path}")
        return 1

    total_chars = 0
    for f in files:
        try:
            total_chars += len(f.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue

    tokens = estimate_tokens(" " * total_chars)  # length-only estimate; content doesn't matter here
    label = args.label or path.name

    entry = {
        "label": label,
        "path": str(path),
        "files_counted": len(files),
        "total_chars": total_chars,
        "estimated_tokens": tokens,
        "estimate_method": f"chars/{CHARS_PER_TOKEN_ESTIMATE}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if args.rate_per_1k is not None:
        entry["estimated_cost_usd"] = round(tokens / 1000 * args.rate_per_1k, 4)

    with LEDGER_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")

    print(f"{label}: {total_chars} chars -> ~{tokens} tokens (estimate)")
    if "estimated_cost_usd" in entry:
        print(f"  ~${entry['estimated_cost_usd']} at ${args.rate_per_1k}/1k")
    print(f"Logged to {LEDGER_FILE}")
    return 0


def _configure_log(p: argparse.ArgumentParser) -> None:
    p.add_argument("-n", type=int, help="Show only the last N entries")


def cmd_log(args: argparse.Namespace) -> int:
    if not LEDGER_FILE.exists():
        print("No ledger yet.")
        return 0
    entries = [json.loads(line) for line in LEDGER_FILE.read_text().splitlines() if line.strip()]
    if args.n:
        entries = entries[-args.n:]
    running_total = 0
    for e in entries:
        running_total += e.get("estimated_tokens", 0)
        cost = f" (~${e['estimated_cost_usd']})" if "estimated_cost_usd" in e else ""
        print(f"{e['timestamp']}  {e['label']:<25} ~{e['estimated_tokens']} tok{cost}")
    print(f"\n{len(entries)} entries. Running total (shown entries): ~{running_total} tokens.")
    return 0


def register(registry) -> None:
    registry.register("token-audit", cmd_audit,
                       help="Estimate and log token count for a file or directory",
                       configure_parser=_configure_audit, source="token_audit")
    registry.register("token-log", cmd_log,
                       help="Show the token audit ledger",
                       configure_parser=_configure_log, source="token_audit")
