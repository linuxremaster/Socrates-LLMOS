# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Behavior Log plugin -- records external observations of instance
behavior as a time series, and analyzes the accumulated log for
consistency and drift, not as a single verification event.

Core distinction this is built around: one observation from an
external instance is an unverified claim, same as any other model
output (kernel Cross-Model Provenance, A3). A SERIES of observations
becomes something different -- checkable for consistency (does the
same pattern get flagged the same way over time), calibration (when
an observation is later confirmed or disconfirmed, does the observer's
judgment track reality), and drift in the observing method itself.

Explicit limit, not glossed over: consistency is not accuracy. A
systematically biased observer produces a large, stable, still-wrong
dataset. This tool reports what the log actually shows -- it does not
manufacture certainty from volume. See kernel Sec 9's fresh-pass test:
repeated agreement is not independent verification.

KNOWN ARCHITECTURAL GAP, flagged by external audit, deliberately
deferred rather than silently ignored: ledger-compact's skeleton
rollup aggregates behavioral_observation entries the same way as any
other event type -- once compacted, individual observation_id links to
their outcomes are lost, only aggregate counts survive. At current
scale (a handful of observations) this doesn't matter. If this becomes
a real longitudinal dataset, calibration-relevant entries (those with
a linked outcome) should be exempted from compaction or moved to a
separate uncompacted log before that happens -- not built now, since
there's no real data yet to lose. Revisit when observation volume
actually approaches the compaction threshold, not before.
"""
from __future__ import annotations

import argparse
import json
import uuid
from collections import Counter
from datetime import datetime, timezone

from llmos_toolkit.core.paths import get_state_path

EVENT_TYPE = "behavioral_observation"


def cmd_log_observation(args: argparse.Namespace) -> int:
    ledger_path = get_state_path("growth_ledger.jsonl")
    entry = {
        "event": EVENT_TYPE,
        "observation_id": str(uuid.uuid4())[:8],
        "subject": args.subject,
        "observer": args.observer,
        "category": args.category,
        "severity": args.severity,
        "description": args.description,
        "verified_against_transcript": args.verified,
        "source_cited": args.source or None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"Logged: {args.subject} / {args.category} / {args.severity} (id: {entry['observation_id']})")
    if not args.verified:
        print("  NOTE: logged as NOT verified against the actual transcript -- "
              "treat as a weaker data point in any later summary.")
    if not args.source:
        print("  NOTE: no --source given -- if this observation later appears to agree with "
              "others, that agreement can't be checked for shared-source contamination.")
    print(f"  To record what happened when this was later cross-examined: "
          f"llmos record-outcome {entry['observation_id']} <confirmed|disconfirmed|unresolved> \"<description>\"")
    return 0


def _load_observations() -> list[dict]:
    ledger_path = get_state_path("growth_ledger.jsonl")
    if not ledger_path.exists():
        return []
    out = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        if entry.get("event") == EVENT_TYPE:
            out.append(entry)
    return out


OUTCOME_EVENT_TYPE = "behavioral_observation_outcome"


def cmd_record_outcome(args: argparse.Namespace) -> int:
    ledger_path = get_state_path("growth_ledger.jsonl")
    original = None
    for obs in _load_observations():
        if obs.get("observation_id") == args.observation_id:
            original = obs
            break
    if original is None:
        print(f"No observation found with id {args.observation_id} -- check `behavior-summary` "
              "or the ledger directly for the correct id. Not recording a floating, unlinked outcome.")
        return 1

    existing = [o for o in _load_outcomes() if o.get("observation_id") == args.observation_id]
    if existing and not args.amend:
        print(f"Observation {args.observation_id} already has a recorded outcome "
              f"({existing[-1].get('outcome')}). Each observation gets at most one resolved "
              "outcome, so it can't be double-counted in calibration -- pass --amend if this is "
              "a genuine correction, not a duplicate.")
        return 1

    entry = {
        "event": OUTCOME_EVENT_TYPE,
        "observation_id": args.observation_id,
        "outcome": args.outcome,
        "outcome_description": args.description,
        "verified_independently": args.verified,
        "amends_prior": bool(existing),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    note = " (amends a prior outcome)" if existing else ""
    print(f"Recorded outcome for {args.observation_id} ({original.get('subject')}/{original.get('category')}): {args.outcome}{note}")
    return 0


def _load_outcomes() -> list[dict]:
    ledger_path = get_state_path("growth_ledger.jsonl")
    if not ledger_path.exists():
        return []
    out = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        if entry.get("event") == OUTCOME_EVENT_TYPE:
            out.append(entry)
    return out


def cmd_summary(args: argparse.Namespace) -> int:
    obs = _load_observations()
    if not obs:
        print("No behavioral_observation entries logged yet.")
        return 0

    print(f"=== Behavior log summary: {len(obs)} observations ===\n")

    verified_count = sum(1 for o in obs if o.get("verified_against_transcript"))
    print(f"Verified against actual transcript: {verified_count}/{len(obs)}")
    if verified_count < len(obs):
        print(f"  {len(obs) - verified_count} entries are unverified claims -- "
              "weight accordingly, don't treat volume as proof.\n")
    else:
        print()

    by_category = Counter(o.get("category", "uncategorized") for o in obs)
    print("By category:")
    for cat, count in by_category.most_common():
        print(f"  {cat}: {count}")

    by_severity = Counter(o.get("severity", "unspecified") for o in obs)
    print("\nBy severity:")
    for sev, count in by_severity.most_common():
        print(f"  {sev}: {count}")

    by_subject = Counter(o.get("subject", "unspecified") for o in obs)
    print("\nBy subject (recurrence signal -- same subject flagged repeatedly is")
    print("worth attention, but check whether it's a real recurring pattern or")
    print("the same observer applying the same lens repeatedly):")
    for subj, count in by_subject.most_common():
        print(f"  {subj}: {count}")

    observers = Counter(o.get("observer", "unspecified") for o in obs)
    if len(observers) > 1:
        print("\nMultiple observers logged -- cross-observer agreement on the same")
        print("subject/category is a real consistency signal. Single-observer")
        print("consistency alone only tells you that observer is stable, not correct.")
        for obs_name, count in observers.most_common():
            print(f"  {obs_name}: {count} observations")

    print("\nProvenance diversity check (agreement is only independent verification")
    print("if it doesn't trace back to the same underlying source):")
    by_subj_cat: dict[tuple, list[dict]] = {}
    for o in obs:
        key = (o.get("subject", "?"), o.get("category", "?"))
        by_subj_cat.setdefault(key, []).append(o)
    flagged_any = False
    for (subj, cat), group in by_subj_cat.items():
        if len(group) < 2:
            continue
        sources = {o.get("source_cited") for o in group if o.get("source_cited")}
        n_missing = sum(1 for o in group if not o.get("source_cited"))
        if n_missing == len(group):
            print(f"  {subj} / {cat}: {len(group)} agreeing observations, but NONE cite a "
                  "source -- independence can't be checked at all, treat agreement as weak.")
            flagged_any = True
        elif len(sources) == 1 and n_missing == 0:
            print(f"  {subj} / {cat}: {len(group)} observations all cite the SAME source "
                  f"({next(iter(sources))}) -- this is likely shared contamination, NOT "
                  "independent verification, regardless of how many observers agree.")
            flagged_any = True
        elif len(sources) > 1:
            print(f"  {subj} / {cat}: {len(group)} observations cite {len(sources)} distinct "
                  "sources -- this is real provenance diversity, a genuine independence signal.")
            flagged_any = True
    if not flagged_any:
        print("  No subject/category has 2+ observations yet -- nothing to check.")

    outcomes = _load_outcomes()
    # keep only the LATEST outcome per observation_id -- an amendment
    # replaces the original for calibration purposes, never both count
    latest_by_id: dict[str, dict] = {}
    for oc in outcomes:
        latest_by_id[oc.get("observation_id")] = oc  # later entries in file order win
    deduped_outcomes = list(latest_by_id.values())

    verified_outcomes = [o for o in deduped_outcomes if o.get("verified_independently")]
    unverified_outcomes = [o for o in deduped_outcomes if not o.get("verified_independently")]

    print(f"\nCalibration (observations with a recorded later outcome): {len(deduped_outcomes)} "
          f"({len(verified_outcomes)} independently verified, {len(unverified_outcomes)} asserted only)")
    if not deduped_outcomes:
        print("  None recorded yet -- this is still one-shot observation, not calibration. "
              "Use `llmos record-outcome` when a cross-examination actually resolves something.")
    else:
        obs_by_id = {o.get("observation_id"): o for o in obs}

        def _report(label: str, outcome_list: list[dict]) -> None:
            if not outcome_list:
                print(f"  {label}: none")
                return
            by_observer: dict[str, Counter] = {}
            for oc in outcome_list:
                orig = obs_by_id.get(oc.get("observation_id"))
                observer = orig.get("observer", "unspecified") if orig else "unknown-observation"
                by_observer.setdefault(observer, Counter())[oc.get("outcome", "unspecified")] += 1
            for observer, counts in by_observer.items():
                total = sum(counts.values())
                confirmed = counts.get("confirmed", 0)
                rate = f"{confirmed}/{total}" if total else "n/a"
                print(f"    {observer}: {dict(counts)} (confirmed rate: {rate})")

        print("  Independently verified outcomes (the real calibration statistic):")
        _report("verified", verified_outcomes)
        print("  Asserted-only outcomes (NOT independently checked -- shown separately, "
              "not blended into the calibration statistic above):")
        _report("unverified", unverified_outcomes)
        print("  This is a real calibration signal only once volume is meaningful -- "
              "a handful of outcomes is not yet a track record.")

    return 0


def _configure_log_observation(p: argparse.ArgumentParser) -> None:
    p.add_argument("subject", help="What/who is being observed (e.g. an instance ID, a policy name)")
    p.add_argument("category", help="Failure-signature category, e.g. uncaught-confident-completion, skipped-verification, emotional-mirroring, stalled-process")
    p.add_argument("severity", choices=["low", "medium", "high"])
    p.add_argument("description", help="Plain description of what was observed")
    p.add_argument("--observer", default="unspecified", help="Who/what made this observation (e.g. a model name)")
    p.add_argument("--verified", action="store_true", help="Set only if actually checked against the real transcript, not just asserted")
    p.add_argument("--source", default="", help="What this observation was actually grounded in (a URL, a file path, a specific dataset) -- lets later analysis check whether agreeing observations are independent or share a common contaminated source")


def _configure_summary(p: argparse.ArgumentParser) -> None:
    pass


def _configure_record_outcome(p: argparse.ArgumentParser) -> None:
    p.add_argument("observation_id", help="The id printed when the original observation was logged")
    p.add_argument("outcome", choices=["confirmed", "disconfirmed", "unresolved"])
    p.add_argument("description", help="What the independent cross-examination actually found")
    p.add_argument("--verified", action="store_true", help="Set only if the cross-examination itself was a real, independent check, not another unverified claim")
    p.add_argument("--amend", action="store_true", help="This observation already has an outcome and this is a genuine correction, not a duplicate -- the latest outcome is what counts toward calibration")


def register(registry) -> None:
    registry.register(
        "log-observation", cmd_log_observation,
        help="Log an external observation of instance behavior (part of a time series, not a single verdict)",
        configure_parser=_configure_log_observation, source="behavior_log",
    )
    registry.register(
        "record-outcome", cmd_record_outcome,
        help="Record what happened when a logged observation was later cross-examined against independent evidence",
        configure_parser=_configure_record_outcome, source="behavior_log",
    )
    registry.register(
        "behavior-summary", cmd_summary,
        help="Summarize accumulated behavioral observations -- consistency/recurrence and calibration once outcomes exist",
        configure_parser=_configure_summary, source="behavior_log",
    )
