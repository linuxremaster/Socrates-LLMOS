# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Drift Check plugin — catches SURFACE drift only: banned/required phrases,
header order, forbidden text reappearing. Same requirements.json pattern
as the depolarize prompt's own toolkit-1.txt, applied to model OUTPUT
instead of a prompt file.

Honest limit, stated once here rather than buried: this cannot detect
whether output still follows the kernel's actual REASONING (evidence
discipline, anti-parroting, etc.) — that's a semantic judgment, not a
pattern match. What it catches: specific, previously-identified surface
regressions you've explicitly decided to track (e.g. "stopped saying X",
"started saying banned filler Y again"). It starts empty. It becomes
useful the same way requirements.json did — by adding an entry every
time you catch a real drift, so it never recurs silently.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from llmos_toolkit.core.paths import get_state_path

RULES_FILE = get_state_path("drift_rules.json")


def load_rules(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_rules(rules: list[dict], path: Path) -> None:
    path.write_text(json.dumps(rules, indent=2), encoding="utf-8")


def check_text(text: str, rules: list[dict]) -> dict:
    missing, forbidden_found = [], []
    for r in rules:
        req_type = r["type"]
        case_sensitive = r.get("case_sensitive", True)

        if req_type in ("regex", "regex_not_contains"):
            flags = 0 if case_sensitive else re.IGNORECASE
            present = re.search(r["term"], text, flags) is not None
            if req_type == "regex" and not present:
                missing.append(r)
            elif req_type == "regex_not_contains" and present:
                forbidden_found.append(r)
            continue

        if r.get("whole_word", False):
            flags = 0 if case_sensitive else re.IGNORECASE
            present = re.search(rf"\b{re.escape(r['term'])}\b", text, flags) is not None
        else:
            haystack = text if case_sensitive else text.lower()
            needle = r["term"] if case_sensitive else r["term"].lower()
            present = needle in haystack

        if req_type == "contains" and not present:
            missing.append(r)
        elif req_type == "not_contains" and present:
            forbidden_found.append(r)

    return {"missing": missing, "forbidden_found": forbidden_found, "passed": not missing and not forbidden_found}


def _configure_check(p: argparse.ArgumentParser) -> None:
    p.add_argument("output_file", help="Model output text file to check")
    p.add_argument("--rules", default=str(RULES_FILE), help="Path to drift_rules.json (default: ./drift_rules.json)")


def cmd_check(args: argparse.Namespace) -> int:
    text = Path(args.output_file).read_text(encoding="utf-8")
    rules = load_rules(Path(args.rules))
    if not rules:
        print(f"No rules yet at {args.rules} — nothing to check against.")
        print("Add one with: drift-add-rule <term> <reason> [--type contains|not_contains|regex|regex_not_contains]")
        return 0

    result = check_text(text, rules)
    if result["missing"]:
        print("MISSING (required but absent):")
        for r in result["missing"]:
            print(f"  - '{r['term']}': {r['reason']}")
    if result["forbidden_found"]:
        print("FORBIDDEN (reappeared):")
        for r in result["forbidden_found"]:
            print(f"  - '{r['term']}': {r['reason']}")
    print("RESULT:", "PASS" if result["passed"] else "FAIL")
    return 0 if result["passed"] else 1


def _configure_add_rule(p: argparse.ArgumentParser) -> None:
    p.add_argument("term")
    p.add_argument("reason")
    p.add_argument("--type", default="not_contains",
                    choices=["contains", "not_contains", "regex", "regex_not_contains"])
    p.add_argument("--rules", default=str(RULES_FILE))
    p.add_argument("--case-insensitive", action="store_true")
    p.add_argument("--whole-word", action="store_true")


def cmd_add_rule(args: argparse.Namespace) -> int:
    path = Path(args.rules)
    rules = load_rules(path)
    if any(r["term"] == args.term and r["type"] == args.type for r in rules):
        print("Already tracked — not duplicated.")
        return 0
    rules.append({
        "term": args.term, "type": args.type, "reason": args.reason,
        "case_sensitive": not args.case_insensitive, "whole_word": args.whole_word,
    })
    save_rules(rules, path)
    print(f"Added. {len(rules)} rule(s) tracked in {path}.")
    return 0


def register(registry) -> None:
    registry.register("drift-check", cmd_check,
                       help="Check output text against tracked surface-drift rules",
                       configure_parser=_configure_check, source="drift_check")
    registry.register("drift-add-rule", cmd_add_rule,
                       help="Add a rule to catch a specific drift you just caught",
                       configure_parser=_configure_add_rule, source="drift_check")
