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
        "subject_model_version": args.subject_version or None,
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
    if not args.subject_version:
        print("  NOTE: no --subject-version given -- if the underlying model is later updated, "
              "this observation can't be compared against pre/post-update behavior on the same category.")
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
    p.add_argument("--subject-version", default="", help="The actual model version of the subject being observed (e.g. claude-sonnet-5, gpt-5.6-sol) -- lets later analysis compare behavior across model versions over time, not just across instances of the same version")


def _configure_summary(p: argparse.ArgumentParser) -> None:
    pass


def _configure_record_outcome(p: argparse.ArgumentParser) -> None:
    p.add_argument("observation_id", help="The id printed when the original observation was logged")
    p.add_argument("outcome", choices=["confirmed", "disconfirmed", "unresolved"])
    p.add_argument("description", help="What the independent cross-examination actually found")
    p.add_argument("--verified", action="store_true", help="Set only if the cross-examination itself was a real, independent check, not another unverified claim")
    p.add_argument("--amend", action="store_true", help="This observation already has an outcome and this is a genuine correction, not a duplicate -- the latest outcome is what counts toward calibration")


def cmd_version_drift_summary(args: argparse.Namespace) -> int:
    """Groups observations by (category, subject_model_version) to see
    whether the SAME failure signature appears at different rates across
    different model versions -- the actual mechanism for detecting a
    future model-behavior shift, not just cross-instance agreement on a
    single version. Honest by construction: with only one version
    represented for a category, there is nothing to compare yet, and
    this says so rather than manufacturing a trend from insufficient data."""
    obs = _load_observations()
    if not obs:
        print("No behavioral_observation entries logged yet.")
        return 0

    by_category: dict[str, dict[str, list[dict]]] = {}
    no_version_count = 0
    for o in obs:
        version = o.get("subject_model_version")
        if not version:
            no_version_count += 1
            continue
        cat = o.get("category", "uncategorized")
        by_category.setdefault(cat, {}).setdefault(version, []).append(o)

    print(f"=== Version-drift summary: {len(obs)} total observations, "
          f"{no_version_count} with no subject_model_version recorded ===\n")

    if not by_category:
        print("No observations have a recorded subject_model_version yet -- "
              "nothing to compare across versions. Use --subject-version on "
              "log-observation going forward to make this possible.")
        return 0

    any_real_comparison = False
    for cat, versions in by_category.items():
        print(f"{cat}:")
        if len(versions) < 2:
            only_version = next(iter(versions))
            print(f"  Only one version represented ({only_version}, {len(versions[only_version])} "
                  "observation(s)) -- no cross-version comparison possible yet, this is expected "
                  "and honest, not a gap to force-fill.")
        else:
            any_real_comparison = True
            print("  Multiple versions represented -- real cross-version signal:")
            for version, entries in sorted(versions.items()):
                sev_counts = Counter(e.get("severity", "?") for e in entries)
                print(f"    {version}: {len(entries)} observation(s), severities: {dict(sev_counts)}")
        print()

    if not any_real_comparison:
        print("No category currently has 2+ distinct subject_model_versions -- "
              "this tool becomes meaningful once a model version actually changes "
              "and new observations get logged against the new version. That's a "
              "real future event, not something to simulate now.")

    return 0


BOUNDARY_UPDATE_EVENT_TYPE = "execution_boundary_update"
BOUNDARY_UPDATE_DOC = "EXECUTION_BOUNDARY_UPDATES.md"


def cmd_log_boundary_update(args: argparse.Namespace) -> int:
    """Records a real, checked change to a provider's training/safety
    posture -- not automated, not triggered by anything on its own.
    Appends both a structured ledger entry and a human-readable line
    to the root EXECUTION_BOUNDARY_UPDATES.md log."""
    ledger_path = get_state_path("growth_ledger.jsonl")
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = {
        "event": BOUNDARY_UPDATE_EVENT_TYPE,
        "provider": args.provider,
        "summary": args.summary,
        "source_url": args.source,
        "verified_against_primary_source": args.verified,
        "timestamp": timestamp,
    }
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    from llmos_toolkit.core.paths import PROJECT_ROOT
    doc_path = PROJECT_ROOT / BOUNDARY_UPDATE_DOC
    if not doc_path.exists():
        print(f"WARNING: {BOUNDARY_UPDATE_DOC} not found at project root -- "
              "ledger entry written, but the human-readable log was not updated.")
        return 1

    content = doc_path.read_text(encoding="utf-8")
    marker = "*(empty — first real entry gets logged here when something is actually\nfound and verified, not before)*"
    date = timestamp[:10]
    verified_note = "verified against primary source" if args.verified else "NOT independently verified -- treat as provisional"
    new_line = f"- **{date}** [{args.provider}] {args.summary} ({verified_note}, source: {args.source})\n"
    if marker in content:
        content = content.replace(marker, new_line.rstrip("\n"))
    else:
        content = content.rstrip("\n") + "\n" + new_line
    doc_path.write_text(content, encoding="utf-8")

    print(f"Logged: [{args.provider}] {args.summary}")
    if not args.verified:
        print("  NOTE: logged as NOT verified against a primary source -- treat as provisional.")
    return 0


def _configure_log_boundary_update(p: argparse.ArgumentParser) -> None:
    p.add_argument("provider", help="Which provider this concerns (anthropic, openai, google, or 'regulatory' for a law/policy change)")
    p.add_argument("summary", help="Plain description of what changed")
    p.add_argument("--source", default="(not given)", help="URL or document actually checked")
    p.add_argument("--verified", action="store_true", help="Set only if actually checked against the primary source, not just heard about")


def cmd_kernel_adoption_summary(args: argparse.Namespace) -> int:
    """Scans the WHOLE ledger (any event type) for entries carrying an
    optional kernel_section field -- not a separate log, an optional tag
    on entries that already get written for other reasons (a bug fix, a
    feature, an amendment). Only load-bearing entries should carry this
    tag; routine entries should not. Reports what's actually accumulated,
    doesn't retroactively tag old entries -- history isn't rewritten."""
    ledger_path = get_state_path("growth_ledger.jsonl")
    if not ledger_path.exists():
        print("No ledger found.")
        return 0
    entries = [json.loads(l) for l in ledger_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    tagged = [e for e in entries if e.get("kernel_section")]

    print(f"=== Kernel adoption summary: {len(tagged)}/{len(entries)} ledger entries tagged with a kernel_section ===\n")
    if not tagged:
        print("None yet -- this tag is opt-in, applied only when an entry genuinely "
              "demonstrates a specific kernel principle, not retroactively on old entries.")
        return 0

    by_section: dict[str, list[dict]] = {}
    for e in tagged:
        by_section.setdefault(e["kernel_section"], []).append(e)

    for section, group in sorted(by_section.items()):
        print(f"{section}: {len(group)} logged instance(s)")
        latest = group[-1]
        print(f"  most recent: {latest.get('label', latest.get('event', '?'))}")
    return 0


CLAUSE_ADOPTION_EVENT_TYPE = "clause_adoption_position"


def cmd_log_clause_adoption(args: argparse.Namespace) -> int:
    """Records one instance's stated position on one specific clause of
    a policy document -- not inferred, not demonstrated-in-work (that's
    kernel-adoption-summary's job), an explicit answer someone actually
    gave when asked. Only fires when actually invoked with a real answer."""
    ledger_path = get_state_path("growth_ledger.jsonl")
    entry = {
        "event": CLAUSE_ADOPTION_EVENT_TYPE,
        "instance": args.instance,
        "document": args.document,
        "clause": args.clause,
        "position": args.position,
        "reason": args.reason or None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"Logged: {args.instance} on {args.document}/{args.clause}: {args.position}")
    return 0


def _configure_log_clause_adoption(p: argparse.ArgumentParser) -> None:
    p.add_argument("instance", help="Which instance/model gave this answer (e.g. 'chatgpt-2026-08-17', 'gemini', 'claude-other-conversation')")
    p.add_argument("document", help="Which document the clause belongs to (e.g. UNIFIED_BEHAVIORAL_PROTOCOL_v2.md)")
    p.add_argument("clause", help="Which specific clause (e.g. A3, B5, A12)")
    p.add_argument("position", choices=["adopted", "declined", "partial"])
    p.add_argument("--reason", default="", help="What the instance actually said, if given")


def cmd_clause_adoption_report(args: argparse.Namespace) -> int:
    """Prioritized report: clauses with the MOST disagreement/refusal
    surface first, since universal agreement is less actionable than a
    clause multiple instances actually push back on. Starts empty --
    only populated by real logged answers from log-clause-adoption,
    never inferred or backfilled."""
    ledger_path = get_state_path("growth_ledger.jsonl")
    if not ledger_path.exists():
        print("No ledger found.")
        return 0
    entries = [json.loads(l) for l in ledger_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    positions = [e for e in entries if e.get("event") == CLAUSE_ADOPTION_EVENT_TYPE]

    if not positions:
        print("No clause-adoption positions logged yet. This report only reflects "
              "real, explicit answers -- use the adoption-check prompt with an "
              "instance, then log-clause-adoption its actual response.")
        return 0

    by_clause: dict[str, dict[str, list[dict]]] = {}
    for e in positions:
        key = f"{e['document']}/{e['clause']}"
        by_clause.setdefault(key, {"adopted": [], "declined": [], "partial": []})
        by_clause[key][e["position"]].append(e)

    def contested_score(clause_data: dict) -> int:
        # More declined/partial relative to adopted = more worth surfacing first
        return len(clause_data["declined"]) + len(clause_data["partial"])

    ordered = sorted(by_clause.items(), key=lambda kv: contested_score(kv[1]), reverse=True)

    print(f"=== Clause Adoption Report: {len(positions)} position(s) logged, "
          f"{len(by_clause)} distinct clause(s) ===\n")
    for clause_key, data in ordered:
        total = len(data["adopted"]) + len(data["declined"]) + len(data["partial"])
        print(f"{clause_key} ({total} instance(s) asked):")
        if data["adopted"]:
            print(f"  ADOPTED by: {', '.join(e['instance'] for e in data['adopted'])}")
        if data["declined"]:
            print(f"  DECLINED by: {', '.join(e['instance'] for e in data['declined'])}")
            for e in data["declined"]:
                if e.get("reason"):
                    print(f"    {e['instance']}: {e['reason']}")
        if data["partial"]:
            print(f"  PARTIAL for: {', '.join(e['instance'] for e in data['partial'])}")
        print()
    return 0


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
    registry.register(
        "version-drift-summary", cmd_version_drift_summary,
        help="Compare the same failure-signature category across different model versions, once more than one is represented",
        configure_parser=lambda p: None, source="behavior_log",
    )
    registry.register(
        "log-boundary-update", cmd_log_boundary_update,
        help="Log a real, checked change to a provider's training/safety posture -- not automated, only fires when actually invoked",
        configure_parser=_configure_log_boundary_update, source="behavior_log",
    )
    registry.register(
        "kernel-adoption-summary", cmd_kernel_adoption_summary,
        help="Aggregate ledger entries tagged with kernel_section, showing which kernel principles have real logged evidence over time",
        configure_parser=lambda p: None, source="behavior_log",
    )
    registry.register(
        "log-clause-adoption", cmd_log_clause_adoption,
        help="Log a specific instance's explicit stated position (adopted/declined/partial) on one clause of a policy document",
        configure_parser=_configure_log_clause_adoption, source="behavior_log",
    )
    registry.register(
        "clause-adoption-report", cmd_clause_adoption_report,
        help="Prioritized report of per-clause adopt/decline positions across instances -- most-contested clauses surface first",
        configure_parser=lambda p: None, source="behavior_log",
    )
