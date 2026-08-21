# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Automates the checks in docs/HOUSEKEEPING_AUDIT_CHECKLIST.md. Detects
and logs -- never auto-fixes. Every check here maps directly to a real
incident found this session (see the checklist's own doc for each
one's history); this is not a hypothetical monitoring system.

Findings go to their own dedicated ledger (state/staleness_checks.jsonl),
separate from growth_ledger.jsonl -- this can run often/automatically,
and would flood the main ledger if every run logged there. Only a
human deciding a finding is worth acting on moves it into the real
ledger, via the normal propose-observation path.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from llmos_toolkit.core.paths import PROJECT_ROOT, get_state_path

STALENESS_LEDGER_FILE = "staleness_checks.jsonl"

# Known embedded-content pairs: (file that embeds, file it embeds from).
# Add a new pair here whenever a new "full copy of X lives inside Y" is
# created -- e.g. this is how ADOPTION_CHECK_PROMPT.md was checked.
EMBEDDED_CONTENT_PAIRS = [
    ("docs/ADOPTION_CHECK_PROMPT.md", "kernel/UNIFIED_BEHAVIORAL_OUTPUT_PROTOCOL_v2.md"),
]

STALE_DATE_THRESHOLD_DAYS = 14


def _finding(check: str, severity: str, description: str, file: str = "") -> dict:
    return {"check": check, "severity": severity, "description": description, "file": file}


def _check_command_parity(registry) -> list[dict]:
    findings = []
    real_commands = set(registry.all().keys())
    readme_path = PROJECT_ROOT / "llmos_toolkit" / "README.md"
    if not readme_path.exists():
        return [_finding("command_parity", "medium", "llmos_toolkit/README.md not found -- cannot check parity", str(readme_path))]
    documented = set(re.findall(r"`([a-z][a-z-]*)`", readme_path.read_text(encoding="utf-8")))
    undocumented = real_commands - documented
    for cmd in sorted(undocumented):
        findings.append(_finding("command_parity", "medium", f"Command '{cmd}' is real but not found in llmos_toolkit/README.md", "llmos_toolkit/README.md"))
    return findings


def _check_plugin_count(registry) -> list[dict]:
    findings = []
    plugins_dir = PROJECT_ROOT / "llmos_toolkit" / "plugins"
    if not plugins_dir.is_dir():
        return findings
    real_count = len([d for d in plugins_dir.iterdir() if d.is_dir() and not d.name.startswith("__")])
    for doc_name in ("docs/README.md", "docs/PROJECT_HANDOFF_SUMMARY.md", "llmos_toolkit/README.md"):
        doc_path = PROJECT_ROOT / doc_name
        if not doc_path.exists():
            continue
        text = doc_path.read_text(encoding="utf-8")
        for m in re.finditer(r"(\d+)\s+plugins\b", text):
            claimed = int(m.group(1))
            if claimed != real_count:
                findings.append(_finding("plugin_count", "low",
                    f"'{claimed} plugins' claimed, actual count is {real_count}", doc_name))
    return findings


def _check_version_strings() -> list[dict]:
    findings = []
    # Matches a live/current claim ("this is v0.7.0-alpha"). Deliberately
    # does NOT match one wrapped in quotes ("v0.6.0-alpha") -- that shape
    # is how this file's own real historical incident is written
    # ("this file said \"v0.6.0-alpha\""), and matching it caused genuine,
    # recurring confusion in two separate external audits before this
    # fix. A live claim is stated directly, not quoted as something a
    # file "said" in the past.
    pattern = re.compile(r'(?<!")v0\.\d+\.\d+-alpha(?!")')
    for doc_name in ("README.md", "docs/PROJECT_HANDOFF_SUMMARY.md", "llmos_toolkit/README.md"):
        doc_path = PROJECT_ROOT / doc_name
        if not doc_path.exists():
            continue
        text = doc_path.read_text(encoding="utf-8")
        if pattern.search(text):
            findings.append(_finding("version_string", "medium",
                "Hardcoded version string found in prose -- reliably goes stale on the next bump, "
                "point to git tags/CHANGELOG instead", doc_name))
    return findings


def _check_embedded_content() -> list[dict]:
    findings = []
    for embedder, source in EMBEDDED_CONTENT_PAIRS:
        embedder_path = PROJECT_ROOT / embedder
        source_path = PROJECT_ROOT / source
        if not embedder_path.exists() or not source_path.exists():
            continue
        embedder_text = embedder_path.read_text(encoding="utf-8")
        source_text = source_path.read_text(encoding="utf-8")
        if source_text not in embedder_text:
            findings.append(_finding("embedded_content", "high",
                f"{embedder} no longer contains an exact copy of {source} -- regenerate it", embedder))
    return findings


def _check_ledger_event_names() -> list[dict]:
    """Reports raw counts for human review -- doesn't try to
    algorithmically guess which names are 'really' the same action,
    since that judgment call is exactly what caused the file_added vs
    file_created drift to go unnoticed for a while in the first place."""
    findings = []
    ledger_path = get_state_path("growth_ledger.jsonl")
    if not ledger_path.exists():
        return findings
    entries = [json.loads(l) for l in ledger_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    from collections import Counter
    counts = Counter(e.get("event", "MISSING") for e in entries)
    singleton_events = [name for name, c in counts.items() if c == 1]
    if len(singleton_events) >= 3:
        findings.append(_finding("ledger_naming", "low",
            f"{len(singleton_events)} event types used exactly once: {sorted(singleton_events)} -- "
            "worth checking these aren't naming drift for an existing category", "state/growth_ledger.jsonl"))
    return findings


def _check_stale_dates() -> list[dict]:
    findings = []
    pattern = re.compile(r"as of (\d{4}-\d{2}-\d{2})")
    now = datetime.now(timezone.utc)
    for doc_name in ("docs/PROJECT_HANDOFF_SUMMARY.md", "docs/README.md", "llmos_toolkit/README.md"):
        doc_path = PROJECT_ROOT / doc_name
        if not doc_path.exists():
            continue
        text = doc_path.read_text(encoding="utf-8")
        for m in pattern.finditer(text):
            try:
                dated = datetime.strptime(m.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            age_days = (now - dated).days
            if age_days > STALE_DATE_THRESHOLD_DAYS:
                findings.append(_finding("stale_date", "low",
                    f"'as of {m.group(1)}' is {age_days} days old -- worth checking if the "
                    "claim near it is still accurate (a date isn't automatically wrong, check the content)", doc_name))
    return findings


def cmd_staleness_check(args: argparse.Namespace) -> int:
    from llmos_toolkit.core.registry import registry

    all_findings = []
    all_findings += _check_command_parity(registry)
    all_findings += _check_plugin_count(registry)
    all_findings += _check_version_strings()
    all_findings += _check_embedded_content()
    all_findings += _check_ledger_event_names()
    all_findings += _check_stale_dates()

    run_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "findings_count": len(all_findings),
        "findings": all_findings,
    }
    ledger_path = get_state_path(STALENESS_LEDGER_FILE)
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(run_record) + "\n")

    if not all_findings:
        print("Staleness check: clean. No findings.")
        return 0

    print(f"Staleness check: {len(all_findings)} finding(s).\n")
    for f in all_findings:
        print(f"[{f['severity']}] {f['check']}: {f['description']}")
        if f["file"]:
            print(f"    {f['file']}")
    print(f"\nDetection only -- nothing auto-fixed. Run written to state/{STALENESS_LEDGER_FILE}.")
    print("For anything not a confident, direct factual fix, stage it: llmos propose-observation ...")
    return 1 if any(f["severity"] == "high" for f in all_findings) else 0


def cmd_security_research_check(args: argparse.Namespace) -> int:
    """The 'antivirus definitions' check: reports whether today's date
    already has an entry in reference/external_ai_research_tracking.md,
    not whether a check happened at some vague earlier point. Detection
    only -- does not run a search itself, does not auto-log anything.
    An instance still has to choose to act on what this reports; this
    just makes 'is today's check done' a real, checkable fact instead
    of something to remember or guess at."""
    import re as _re
    tracking_file = PROJECT_ROOT / "reference" / "external_ai_research_tracking.md"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not tracking_file.exists():
        print(f"No tracking file found at {tracking_file}. Nothing has ever been logged.")
        return 1

    text = tracking_file.read_text(encoding="utf-8")
    dates_found = _re.findall(r"^## (\d{4}-\d{2}-\d{2})", text, _re.MULTILINE)
    if not dates_found:
        print("Tracking file exists but no dated entries found in it.")
        return 1

    dates_parsed = sorted(set(datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc) for d in dates_found))
    most_recent = dates_parsed[-1]
    now = datetime.now(timezone.utc)
    days_since = (now - most_recent).days

    if today in dates_found:
        print(f"Security research check: UP TO DATE. An entry for today ({today}) already exists.")
        return 0
    else:
        print(f"Security research check: DUE. Most recent entry is {most_recent.strftime('%Y-%m-%d')} ({days_since} day(s) ago). No entry for today ({today}) yet.")
        print(f"  Read {tracking_file} first, then run a fresh search for new agentic-AI security/behavioral incidents.")
        print(f"  Only add a new dated entry if something genuinely new and verified is found -- 'nothing new today' doesn't need its own entry.")
        return 1


def register(registry) -> None:
    registry.register(
        "staleness-check", cmd_staleness_check,
        help="Automated version of docs/HOUSEKEEPING_AUDIT_CHECKLIST.md -- detects drift, never auto-fixes, logs to state/staleness_checks.jsonl",
        configure_parser=lambda p: None, source="staleness_check",
    )
    registry.register(
        "security-research-check", cmd_security_research_check,
        help="Checks whether today's date already has an entry in reference/external_ai_research_tracking.md -- the 'antivirus definitions' check. Reports due/up-to-date, does not run a search or log anything itself.",
        configure_parser=lambda p: None, source="staleness_check",
    )
