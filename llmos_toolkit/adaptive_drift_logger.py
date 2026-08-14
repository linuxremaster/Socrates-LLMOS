#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Adaptive Drift Logger

Implements the five drift classes from ADAPTIVE_DRIFT_LOGGER_README.md:
growth/bloat, semantic, cross-artifact, embedded-vs-standalone, and
numbering/structural.

Design constraints, carried over from the spec and stated here so the
code's intent is legible without re-reading the README:

- Cross-artifact checks compare LABELLED reference fields only (lines of
  the form "**Label:** value") — never generic proximity/similarity
  matching, which is what produced false-positive floods before.
- Semantic changes are never auto-resolved. Textual similarity is never
  promoted to semantic equivalence. A changed section is always a review
  finding; it clears only when the baseline is explicitly retaken
  (--rebaseline), never by suppression.
- Self-adaptation is conservative: a finding's signature is tracked
  across runs (times observed), but its severity/suppression status
  changes ONLY on an explicit --confirm from a human. Repetition alone
  never promotes a finding to "confirmed" — that would let the logger
  learn its own false positives as truth, which is the one thing this
  is designed not to do.

Usage:
    python adaptive_drift_logger.py path/to/kernel.md
    python adaptive_drift_logger.py kernel.md adapter.md global_check.md
    python adaptive_drift_logger.py kernel.md --rebaseline
    python adaptive_drift_logger.py --list-signatures
    python adaptive_drift_logger.py --confirm SIGNATURE_ID --as real|false_positive

Exit codes:
    0  no findings
    1  findings requiring review
    2  high-severity finding requiring review
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

STATE_FILE = Path(".drift_state.json")
AUDIT_FILE = Path("drift_audit.jsonl")

HEADER_RE = re.compile(r"^#{1,6}\s*(\d+)\.\s*(.*)$", re.MULTILINE)
LABELLED_FIELD_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z0-9 /_\-]{1,40}):\*\*\s*(.+)$", re.MULTILINE)
EMBEDDED_MARKER_RE = re.compile(
    r"<!--\s*embedded-from:\s*(\S+?)\s*-->\s*\n```[a-zA-Z]*\n(.*?)```",
    re.DOTALL,
)

# Labels where a mismatch across artifacts is worth flagging. Deliberately
# a small, explicit list rather than "any label that appears twice" — an
# unlisted shared label (e.g. "Purpose") legitimately differing between
# two unrelated documents isn't drift.
CROSS_ARTIFACT_WATCH_LABELS = {
    "Derivation", "Status", "Version", "Kernel control", "Canonical",
    "Depends On", "Document ID",
}


# ---------------------------------------------------------------------------
# Snapshotting
# ---------------------------------------------------------------------------

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_headers(text: str) -> list[dict]:
    """Numbered headers in order of appearance, with each section's body
    (from end of this header line to start of the next) hashed for
    semantic-change detection."""
    matches = list(HEADER_RE.finditer(text))
    headers = []
    for i, m in enumerate(matches):
        number, title = m.group(1), m.group(2).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end]
        headers.append({
            "number": number,
            "title": title,
            "body_sha256": sha256_text(body),
        })
    return headers


def parse_labelled_fields(text: str) -> dict:
    fields = {}
    for m in LABELLED_FIELD_RE.finditer(text):
        label, value = m.group(1).strip(), m.group(2).strip()
        fields[label] = value  # last occurrence wins if repeated in-file
    return fields


def parse_embedded_refs(text: str) -> list[dict]:
    refs = []
    for m in EMBEDDED_MARKER_RE.finditer(text):
        ref_path, block = m.group(1), m.group(2)
        refs.append({"source_path": ref_path, "block_sha256": sha256_text(block)})
    return refs


def snapshot_artifact(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return {
        "path": str(path),
        "sha256": sha256_text(text),
        "lines": len(text.splitlines()),
        "chars": len(text),
        "headers": parse_headers(text),
        "labelled_fields": parse_labelled_fields(text),
        "embedded_refs": parse_embedded_refs(text),
        "snapshotted_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    check_class: str            # growth | semantic | cross_artifact | embedded | structural
    severity: str                # "high" (never suppressible) or "review" (confirmable)
    description: str
    artifact: str
    signature_key: str           # stable identity for this specific finding, for the learning loop


def check_structural(snapshot: dict) -> list[Finding]:
    findings = []
    numbers = [int(h["number"]) for h in snapshot["headers"]]
    seen = set()
    for n in numbers:
        if n in seen:
            findings.append(Finding(
                "structural", "high",
                f"Duplicate header number {n}",
                snapshot["path"], f"structural:dup:{snapshot['path']}:{n}",
            ))
        seen.add(n)
    if numbers:
        expected = set(range(min(numbers), max(numbers) + 1))
        gaps = sorted(expected - set(numbers))
        for g in gaps:
            findings.append(Finding(
                "structural", "review",
                f"Header numbering gap at {g} (present: {min(numbers)}-{max(numbers)})",
                snapshot["path"], f"structural:gap:{snapshot['path']}:{g}",
            ))
    return findings


def check_growth(baseline: dict, current: dict) -> list[Finding]:
    findings = []
    delta = current["lines"] - baseline["lines"]
    if delta > 0:
        findings.append(Finding(
            "growth", "review",
            f"Grew {delta:+d} lines since baseline ({baseline['lines']} -> {current['lines']})",
            current["path"], f"growth:{current['path']}",
        ))
    return findings


def check_semantic(baseline: dict, current: dict) -> list[Finding]:
    """Never suppressible — a changed section is always surfaced. Clears
    only via --rebaseline, which is an explicit human act of review."""
    findings = []
    baseline_by_number = {h["number"]: h for h in baseline["headers"]}
    for h in current["headers"]:
        prior = baseline_by_number.get(h["number"])
        if prior is None:
            findings.append(Finding(
                "semantic", "review",
                f"New section {h['number']}. {h['title']} — needs review, not auto-cleared",
                current["path"], f"semantic:new:{current['path']}:{h['number']}",
            ))
        elif prior["body_sha256"] != h["body_sha256"]:
            findings.append(Finding(
                "semantic", "review",
                f"Section {h['number']}. {h['title']} content changed — "
                f"textual diff only, meaning not evaluated. Needs human review.",
                current["path"], f"semantic:changed:{current['path']}:{h['number']}",
            ))
    for number, prior in baseline_by_number.items():
        if number not in {h["number"] for h in current["headers"]}:
            findings.append(Finding(
                "semantic", "review",
                f"Section {number}. {prior['title']} removed since baseline",
                current["path"], f"semantic:removed:{current['path']}:{number}",
            ))
    return findings


def check_cross_artifact(snapshots: list[dict]) -> list[Finding]:
    findings = []
    by_label: dict[str, list[tuple[str, str]]] = {}
    for snap in snapshots:
        for label, value in snap["labelled_fields"].items():
            if label not in CROSS_ARTIFACT_WATCH_LABELS:
                continue
            by_label.setdefault(label, []).append((snap["path"], value))

    for label, occurrences in by_label.items():
        if len(occurrences) < 2:
            continue
        values = {v for _, v in occurrences}
        if len(values) > 1:
            detail = "; ".join(f"{p}='{v}'" for p, v in occurrences)
            sig = "cross_artifact:" + "|".join(sorted(p for p, _ in occurrences)) + f":{label}"
            findings.append(Finding(
                "cross_artifact", "review",
                f"Label '{label}' disagrees across artifacts: {detail}",
                ", ".join(p for p, _ in occurrences), sig,
            ))
    return findings


def check_embedded(snapshots: list[dict]) -> list[Finding]:
    """High severity, never suppressible — an exact-content mismatch
    against an explicitly labelled source is mechanically unambiguous."""
    findings = []
    by_path = {snap["path"]: snap for snap in snapshots}
    for snap in snapshots:
        for ref in snap["embedded_refs"]:
            source = by_path.get(ref["source_path"])
            if source is None:
                findings.append(Finding(
                    "embedded", "review",
                    f"Embedded-from reference to '{ref['source_path']}' — "
                    f"source not among supplied artifacts, cannot verify",
                    snap["path"], f"embedded:unresolved:{snap['path']}:{ref['source_path']}",
                ))
                continue
            if ref["block_sha256"] != source["sha256"]:
                findings.append(Finding(
                    "embedded", "high",
                    f"Embedded copy in {snap['path']} no longer matches standalone source {ref['source_path']}",
                    snap["path"], f"embedded:mismatch:{snap['path']}:{ref['source_path']}",
                ))
    return findings


# ---------------------------------------------------------------------------
# State (baseline snapshots + learned signatures)
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"baselines": {}, "signatures": {}}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def append_audit(entry: dict) -> None:
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def update_signature(state: dict, finding: Finding) -> dict:
    """Track observation count for a finding's signature. Status changes
    ONLY via explicit --confirm — never automatically, regardless of how
    many times this signature has been observed."""
    sig = state["signatures"].setdefault(finding.signature_key, {
        "check_class": finding.check_class,
        "description": finding.description,
        "first_seen": datetime.now(timezone.utc).isoformat(),
        "times_observed": 0,
        "status": "unconfirmed",  # unconfirmed | confirmed_real | confirmed_false_positive
        "confirmed_at": None,
    })
    sig["times_observed"] += 1
    sig["last_seen"] = datetime.now(timezone.utc).isoformat()
    sig["description"] = finding.description  # keep latest wording
    return sig


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_run(paths: list[str], rebaseline: bool) -> int:
    artifact_paths = [Path(p) for p in paths]
    for p in artifact_paths:
        if not p.is_file():
            print(f"Not a file: {p}", file=sys.stderr)
            return 2

    state = load_state()
    snapshots = [snapshot_artifact(p) for p in artifact_paths]
    all_findings: list[Finding] = []

    # Structural, cross-artifact, and embedded checks compare artifacts to
    # themselves/each other right now — they need no history, so they run
    # (and are reported) even on a first run or a --rebaseline.
    for snap in snapshots:
        all_findings.extend(check_structural(snap))
    all_findings.extend(check_cross_artifact(snapshots))
    all_findings.extend(check_embedded(snapshots))

    # Growth and semantic checks are genuinely baseline-dependent — only
    # these are skipped per-artifact when no prior baseline exists yet.
    newly_baselined = []
    for snap in snapshots:
        key = snap["path"]
        baseline = state["baselines"].get(key)
        if baseline is None or rebaseline:
            state["baselines"][key] = snap
            newly_baselined.append(key)
            continue
        all_findings.extend(check_growth(baseline, snap))
        all_findings.extend(check_semantic(baseline, snap))

    if newly_baselined:
        verb = "Re-baselined" if rebaseline else "Baseline established for"
        print(f"{verb}: {', '.join(newly_baselined)} "
              f"(growth/semantic comparison starts next run for these).")

    visible: list[tuple[Finding, dict]] = []
    suppressed_count = 0
    high_present = False
    review_present = False

    for finding in all_findings:
        sig = update_signature(state, finding)

        if finding.severity == "high":
            high_present = True
            visible.append((finding, sig))
            continue

        # review-severity: suppressible only via explicit confirm
        if sig["status"] == "confirmed_false_positive":
            suppressed_count += 1
            continue
        if sig["status"] == "confirmed_real":
            high_present = True  # a human already confirmed this matters — escalate
        else:
            review_present = True
        visible.append((finding, sig))

    save_state(state)

    for finding, sig in visible:
        marker = {"high": "[HIGH]", "review": "[REVIEW]"}[finding.severity if sig["status"] != "confirmed_real" else "high"]
        print(f"{marker} ({finding.check_class}) {finding.description}")
        print(f"    signature: {finding.signature_key}  observed: {sig['times_observed']}x  status: {sig['status']}")

    if suppressed_count:
        print(f"\n({suppressed_count} finding(s) suppressed — confirmed false positive)")

    if not visible:
        print("No findings.")

    append_audit({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "artifacts": [str(p) for p in artifact_paths],
        "action": "check",
        "newly_baselined": newly_baselined,
        "findings": [
            {"check_class": f.check_class, "severity": f.severity, "description": f.description,
             "signature": f.signature_key, "status": sig["status"]}
            for f, sig in visible
        ],
        "suppressed_count": suppressed_count,
    })

    if high_present:
        return 2
    if review_present or any(sig["status"] == "confirmed_real" for _, sig in visible):
        return 1
    return 0 if not visible else 1


def cmd_list_signatures() -> int:
    state = load_state()
    sigs = state.get("signatures", {})
    if not sigs:
        print("No signatures tracked yet.")
        return 0
    for key, sig in sorted(sigs.items()):
        print(f"{key}")
        print(f"    [{sig['check_class']}] {sig['description']}")
        print(f"    observed: {sig['times_observed']}x  status: {sig['status']}")
    return 0


def cmd_confirm(signature_id: str, as_status: str) -> int:
    status_map = {"real": "confirmed_real", "false_positive": "confirmed_false_positive"}
    if as_status not in status_map:
        print("--as must be 'real' or 'false_positive'", file=sys.stderr)
        return 2
    state = load_state()
    if signature_id not in state["signatures"]:
        print(f"Unknown signature: {signature_id}", file=sys.stderr)
        return 2
    sig = state["signatures"][signature_id]
    if sig["check_class"] == "semantic" and as_status == "false_positive":
        print(
            "Refused: a 'semantic' signature cannot be confirmed as a false positive. "
            "Doing so would mean asserting the meaning didn't change based on this "
            "tool's textual diff alone — exactly what it's designed not to do. "
            "If the content change has been reviewed and is fine, clear it with "
            "--rebaseline instead, which is an explicit human act of review.",
            file=sys.stderr,
        )
        return 2
    sig["status"] = status_map[as_status]
    sig["confirmed_at"] = datetime.now(timezone.utc).isoformat()
    save_state(state)
    print(f"Confirmed {signature_id} as {status_map[as_status]}.")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("artifacts", nargs="*", help="Markdown files to check")
    parser.add_argument("--rebaseline", action="store_true", help="Reset the baseline to the current file contents")
    parser.add_argument("--list-signatures", action="store_true", help="List all tracked finding signatures")
    parser.add_argument("--confirm", metavar="SIGNATURE_ID", help="Confirm a signature's status")
    parser.add_argument("--as", dest="as_status", choices=["real", "false_positive"], help="Status for --confirm")
    args = parser.parse_args(argv)

    if args.list_signatures:
        return cmd_list_signatures()
    if args.confirm:
        if not args.as_status:
            print("--confirm requires --as real|false_positive", file=sys.stderr)
            return 2
        return cmd_confirm(args.confirm, args.as_status)
    if not args.artifacts:
        parser.print_help()
        return 2
    return cmd_run(args.artifacts, args.rebaseline)


if __name__ == "__main__":
    sys.exit(main())
