# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Claim Flag plugin — advisory pattern scan for two things worth a human
second look: absolute/overconfident language, and sentences that look
like factual claims (numbers, dates, named entities) with no nearby
hedge or source marker.

This is NOT a hallucination detector. It cannot check whether a claim is
TRUE — that needs actual verification against a source, which this tool
doesn't do. It only flags sentences worth checking by hand, the same way
the security plugin's static_scan flags code worth a human look rather
than clearing it. Expect false positives (accurate claims get flagged)
and false negatives (confident wrong claims with no absolute language
slip through untouched) — that is the nature of a pattern match, not a
bug to fix.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ABSOLUTE_PATTERNS = [
    r"\balways\b", r"\bnever\b", r"\bdefinitely\b", r"\bguaranteed?\b",
    r"\bproven?\b", r"\bundeniably\b", r"\b100%\b", r"\bimpossible\b",
    r"\bcertainly\b", r"\bwithout (a )?doubt\b", r"\ball \w+ (are|do|have)\b",
]

HEDGE_OR_SOURCE_PATTERNS = [
    r"\baccording to\b", r"\bsource[sd]?\b", r"\bcite[sd]?\b", r"\bhttps?://",
    r"\b(verified|inferred|assumed|unknown)\b", r"\bmight\b", r"\bmay\b",
    r"\bpossibly\b", r"\bappears? to\b", r"\bsuggests?\b", r"\bI think\b",
    r"\bestimated?\b", r"\breportedly\b",
]

FACTUAL_SHAPE_PATTERNS = [
    r"\b\d{4}\b",            # a year or 4-digit number
    r"\b\d+(\.\d+)?%\b",     # a percentage
    r"\b\d+(\.\d+)?\b.*\b(million|billion|thousand)\b",
    r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # crude proper-noun-pair heuristic (Named Entity-ish)
]

_ABS_RE = re.compile("|".join(ABSOLUTE_PATTERNS), re.IGNORECASE)
_HEDGE_RE = re.compile("|".join(HEDGE_OR_SOURCE_PATTERNS), re.IGNORECASE)
_FACT_RE = re.compile("|".join(FACTUAL_SHAPE_PATTERNS))


def split_sentences(text: str) -> list[str]:
    # Deliberately simple — good enough for flagging, not for NLP correctness.
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def scan_text(text: str) -> list[dict]:
    findings = []
    for sentence in split_sentences(text):
        reasons = []
        if _ABS_RE.search(sentence):
            reasons.append("ABSOLUTE_LANGUAGE")
        if _FACT_RE.search(sentence) and not _HEDGE_RE.search(sentence):
            reasons.append("UNSOURCED_FACTUAL_SHAPE")
        if reasons:
            findings.append({"sentence": sentence, "reasons": reasons})
    return findings


def _configure_flag(p: argparse.ArgumentParser) -> None:
    p.add_argument("output_file", help="Model output text file to scan")


def cmd_flag(args: argparse.Namespace) -> int:
    text = Path(args.output_file).read_text(encoding="utf-8")
    findings = scan_text(text)
    if not findings:
        print("No pattern matches. This does NOT mean the text is accurate —")
        print("only that nothing matched these specific patterns.")
        return 0
    print(f"{len(findings)} sentence(s) flagged for review:")
    for f in findings:
        print(f"  [{', '.join(f['reasons'])}] {f['sentence']}")
    print()
    print("Reminder: pattern match only, not verification. Check these by hand.")
    return 0


def register(registry) -> None:
    registry.register("flag-claims", cmd_flag,
                       help="Advisory scan for absolute language and unsourced factual claims",
                       configure_parser=_configure_flag, source="claim_flag")
