# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Paste Handoff plugin -- generates a short, plaintext orientation block
meant to be copy-pasted directly into a fresh conversation's first
message, not attached as a file. A file attachment (even a small one)
still counts against the platform's per-conversation attachment cap;
pasted text does not. Built specifically to reduce how many attachment
slots a session-to-session handoff costs -- the project zip still
needs uploading once, but this replaces the extra screenshots/files
that would otherwise be spent re-explaining current state.

Deliberately short: git log tail, current tag, last few real (non-
skeleton) ledger entries, and the open-items section from the handoff
doc if present. Not a substitute for the full project -- a primer to
send alongside the one necessary zip upload.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from llmos_toolkit.core.paths import PROJECT_ROOT, get_state_path


def _git(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT)] + args,
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def _recent_ledger_entries(n: int = 5) -> list[dict]:
    ledger_path = get_state_path("growth_ledger.jsonl")
    if not ledger_path.exists():
        return []
    lines = [ln for ln in ledger_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    entries = [json.loads(ln) for ln in lines]
    non_skeleton = [e for e in entries if e.get("event") != "ledger_skeleton_summary"]
    return non_skeleton[-n:]


def _open_items_section() -> str:
    handoff_doc = PROJECT_ROOT / "docs" / "PROJECT_HANDOFF_SUMMARY.md"
    if not handoff_doc.exists():
        return "(docs/PROJECT_HANDOFF_SUMMARY.md not found)"
    text = handoff_doc.read_text(encoding="utf-8")
    marker = "## 6. Known open items"
    idx = text.find(marker)
    if idx == -1:
        return "(open-items section not found -- check docs/PROJECT_HANDOFF_SUMMARY.md directly)"
    next_section = text.find("\n## ", idx + len(marker))
    section = text[idx:next_section if next_section != -1 else idx + 1500]
    return section.strip()[:1200]


def cmd_paste_handoff(args: argparse.Namespace) -> int:
    tag = _git(["describe", "--tags", "--abbrev=0"]) or "(no tag)"
    log = _git(["log", "--oneline", "-5"]) or "(no commits found)"
    entries = _recent_ledger_entries()

    lines = [
        f"=== {PROJECT_ROOT.name} -- paste handoff ({tag}) ===",
        "",
        "Recent commits:",
        log,
        "",
        "Recent ledger activity:",
    ]
    for e in entries:
        label = e.get("label", e.get("event", "?"))
        lines.append(f"- {e.get('event', '?')}: {label}")

    lines += ["", "Open items (from docs/PROJECT_HANDOFF_SUMMARY.md):", _open_items_section()]
    lines += [
        "",
        "=== end handoff -- upload the project zip alongside this, don't",
        "    re-explain state with screenshots, ask directly if unclear ===",
    ]

    output = "\n".join(lines)
    print(output)
    if args.save:
        out_path = get_state_path("PASTE_HANDOFF.txt")
        out_path.write_text(output, encoding="utf-8")
        print(f"\n[also saved to {out_path}]")
    return 0


def _configure_paste_handoff(p: argparse.ArgumentParser) -> None:
    p.add_argument("--save", action="store_true", help="Also save to state/PASTE_HANDOFF.txt")


def register(registry) -> None:
    registry.register(
        "paste-handoff", cmd_paste_handoff,
        help="Print a short copy-paste-ready handoff block (no file attachment needed)",
        configure_parser=_configure_paste_handoff, source="paste_handoff",
    )
