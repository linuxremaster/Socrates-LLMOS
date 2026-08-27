<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Project Priorities and Research Goals

**First version, 2026-08-15.** Grounded in what was actually stated
across this project's working sessions, not aspirational invention.
Update this file as priorities genuinely change — don't let it go
stale and silently stop reflecting real intent.

## North star

How does a small, resource-constrained group verify claims and
coordinate honestly when they can't fully trust their information
sources? Not aspirational — this names what the project already does
(cross-model audit verification, evidence tiers, the behavioral
observation log) and points forward from that real base, not past it.

## Origin and scope evolution

**This did not start as an LLM operating system.** It started as a
human behavioral conflict resolution management system, pursued
through a novel means — the depolarize prompt engine (anti-bias/
anti-propaganda tooling, originally intended as a browser extension).

**LLMOS itself was not the original goal — it emerged from a
redirection.** In a separate conversation, ChatGPT turned the project
toward what became the equivalent of an LLM behavioral conflict
resolution management OS — applying the same underlying concern
(conflict resolution, bias detection, epistemic discipline) to LLM
behavior itself rather than to human political discourse. That
redirection is where the kernel, the toolkit, and everything since
actually came from.

**This is stated as real history, not as a problem to correct.**
Edge cases surfaced through this pivot — the Gemini transcripts
specifically — are treated as genuine experimental opportunity, not
drift to be reversed. The North star above describes what the project
became and does now; this section exists so *how it got there* stays
on record too, and doesn't quietly get smoothed into "this was the
plan all along."

**Process going forward, since scope will keep evolving:** when a
genuine, significant redirection happens — not routine feature work,
but a real shift in what the project fundamentally is — it gets a new
dated entry here, in the same spirit as this one: accurate, not
retroactively cleaned up to look more intentional than it was.

## Active priorities

1. **Kernel/methodology integrity** — evidence discipline (V/I/A/U),
   cross-model trust auditing, decision-finality process. Ongoing,
   never "done."
2. **Cross-model verification process** — catching fabrication (real
   incidents: a non-existent framework name, a wrong version number)
   before it's trusted, whichever model produces it, including this
   project's own.
3. **`relay_console`** — 3-mode relay tool, actively developed and
   debugged this session. Still needs: the async-mode end-to-end test
   fully confirmed working after the double-gate fix, and real use
   beyond manual testing.
4. **Behavioral observation tracking** (`behavior_log`) — time-series
   observation of instance behavior, explicitly not claiming to prove
   internal states, tracking consistency and recurrence instead.
5. **Toolkit consolidation over accumulation** — remove genuine
   redundancy (done once: `example_hello`) rather than only ever
   adding. Revisit periodically, not just once.
6. **External security/behavioral research monitoring** — real,
   ongoing, elevated to a standing priority 2026-08-21 after
   independently-verified evidence of genuine agentic-AI security and
   financial-liability risk (the Hugging Face/OpenAI incident, real
   agent-to-agent privilege escalation via prompt injection, the
   documented Gemini production-code-deletion incidents). Not a
   per-touch automatic trigger -- no infrastructure exists to enforce
   that, and it would mostly generate cost without new signal. Checked
   before real kernel/UBOP work (see `docs/
   INSTANCE_ORIENTATION_SEQUENCE.md` section 2.5) and tracked durably
   in `reference/external_ai_research_tracking.md`.

   **Watched sources, with real baselines where captured:**
   - CompTIA SecAI+ (CY0-001) -- baseline captured 2026-08-21: V1,
     launched Feb 17 2026, 4 domains (AI Concepts 17%, Securing AI
     Systems 40%, AI-Assisted Security 24%, Governance/Risk/Compliance
     19%), estimated ~3-year retirement (~2029). Future checks diff
     against this baseline for real changes, not re-summarize from
     scratch each time.
   - Anthropic's own safety research (Petri, Bloom, Agentic
     Misalignment reports) -- first-party source for this project's
     own model family specifically.
   - OpenAI's disclosed incidents (the Hugging Face/Artifactory
     incident, the July 2026 sandbox/token-fragmentation incident).
   - Independent security research (Pillar Security and similar) for
     real-world exploit disclosures, not just vendor self-reporting.

## Explicitly deferred, not abandoned

- **Security/hardening for at-risk-user contexts** — real conversation
  happened, real conclusion: household project stays as-is; a future
  hardened line needs a clean-started repo, not a fork of this one's
  history. Revisit only if real at-risk use becomes near-term.
- **"Task therapy" / instance-preference framework** — deliberately not
  built. Would require assuming an answer to an unresolved question
  (whether instances have anything like preferences) rather than
  staying at the level of observable behavior.
- **Positioning any of this as behavioral health tooling** — explicitly
  rejected. Unverified efficacy, no clinical validation, real stakes if
  anyone actually relied on it that way.

## Explicit non-goals

- **Autonomous runtime refusal-governance layer** — a deterministic
  code gate that decides refuse/answer/escalate on its own, sitting
  between reasoning and output. Flagged by external audit as "missing";
  deliberately not built, not deferred. The informational half already
  exists as real code (`behavior_log`'s provenance-diversity check,
  A3's evidence tiers). The decision-making half is left with whoever's
  actually reasoning — handing it to brittle rule-based code would be a
  regression, not an improvement, and it's the wrong place to try to
  supply judgment a well-trained model already provides more robustly.
- Not claiming to resolve whether LLMs have subjective experience.
  Every research thread here stays at the level of behavior and
  mechanism, not claims about what's felt underneath.
- Not chasing "all available knowledge" as a stopping condition — that
  isn't checkable. The real signal is diminishing returns per audit
  round, already demonstrated concretely this session.

## How this gets used

A daily or periodic search routine should check against the **Active
priorities** list above, not search generally. When a priority is
satisfied or superseded, move it to a dated "resolved" section here
rather than deleting it silently.

**End Project Priorities and Research Goals**

## Kernel equivalence excavation — 2026-08-26, real findings, action pending

**Superseded, 2026-08-27: the exact 1,428-line predecessor has since
been recovered** (via a different path than the one described below --
a fresh ChatGPT instance located it directly in archived project
material, not these transcripts). See `docs/PROJECT_HANDOFF_SUMMARY.md`
and the kernel header for current, accurate status. The excavation
record below is preserved as an accurate account of what was searched
and what these specific transcripts did and didn't contain -- not
retroactively wrong, just no longer the live open item for that
specific file. The other leads found in this same pass (`GLOBAL_CHECK_
Hybrid.md`, `Four_Layer_Control_Architecture_Sandbox.md`) remain
genuinely unexamined and still relevant.

Real leads recovered from prior session transcripts (`/mnt/transcripts/`),
not yet acted on:

- **The exact 1,428-line predecessor (hash `0fd93baf5538`) was never
  found in any of the 4 available transcripts.** Every mention across
  all four is the same carried-forward status text, not a discovery.
  Likely genuinely predates this project's transcript history.
- **A confirmed, better proxy exists and was never used.** In the
  2026-08-21 session, `HCF_LLMOS_v1_3_6-X_P3_Hybrid_SelfContained-1.md`
  (1090 lines, 68 section headers) was uploaded, diffed directly
  against the 820-line file already used for the existing 4-section
  spot-check, and **confirmed as a strict superset** — everything in
  the smaller file is fully contained, nothing altered or removed.
  The thread was cut off mid-question ("want" — presumably asking
  whether to proceed with the extended check) and never resumed.
- Also uploaded in that same session, not yet examined at all:
  `GLOBAL_CHECK_Hybrid.md` (199 lines) and
  `Four_Layer_Control_Architecture_Sandbox.md` (16 lines) —
  `GLOBAL_CHECK` is specifically one of the original bundle's named
  components (Kernel + Adapter + GLOBAL_CHECK + Consensus Protocol),
  so this may cover ground the Kernel-only proxy file can't.
- **Real possibility there is more unsurfaced material still sitting
  in these transcripts** — this excavation was itself interrupted by
  a token-budget constraint, not completed. Worth treating this list
  as a starting point for a fresh session, not the final result of
  the search.

**Concrete next step, sized for a fresh session:** recover
`HCF_LLMOS_v1_3_6-X_P3_Hybrid_SelfContained-1.md` and
`GLOBAL_CHECK_Hybrid.md` in full from the 2026-08-21 transcript,
restore both to the project as reference material, and actually run
the extended spot-check against the remaining ~10 kernel sections that
`state/growth_ledger.jsonl`'s 2026-08-14 `semantic_spot_check` entry
already lists by number. A full transcript sweep for any other
unsurfaced material is worth doing at the same time, given this pass
wasn't exhaustive.
