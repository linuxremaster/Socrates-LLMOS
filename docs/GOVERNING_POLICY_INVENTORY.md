<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Socrates / Organic LLMOS — Governing Policy Inventory

**Status:** REFERENCE / NON-CANONICAL
**Purpose:** Single glance-able map of what governing policies exist,
  what their status is, where they live, and what's still needed.
  Produced 2026-09-11 from direct repo inspection.
**Authority note:** This inventory is a map, not a territory. The
  adopted artifacts govern their own scopes. This document describes
  their status; it does not substitute for them.

---

## TIER 1 — CANONICAL (authoritative, unchanged pending formal succession)

| Artifact | Location | Notes |
|---|---|---|
| `HCF_LLMOS_Kernel_v1.3.6-C.md` | `kernel/` | SHA `9948cc95...` — primary behavioral/epistemic methodology. SPOT-CHECKED partial only (~6/21 predecessor sections). |
| `UNIFIED_BEHAVIORAL_OUTPUT_PROTOCOL_v2.md` | `kernel/` | Subordinate to host/system constraints. Output-shape convention. |
| `SEMANTIC_DRIFT_POLICY.md` | `kernel/` | Drift detection companion. |
| `ARTIFACT_DELTA_LOOP_DETECTION_POLICY.md` | `kernel/` | Loop/recurrence detection companion. |
| `DECISION_FINALITY_POLICY.md` | `kernel/` | Prevents re-opening closed decisions without new evidence. |
| `WELLBEING_FLAG_HANDLING_ADDENDUM.md` | `kernel/` | Wellbeing/distress handling addendum. |
| `LLMOS_LEDGER_SECURITY_SPEC.md` | `docs/` | Canonical where it and any draft conflict. |
| `TELEMETRY_CANVAS_LLMOS_RELATIONSHIP.md` | `docs/` | Adopted 2026-08-29. Canvas is bridge not runtime. |

---

## TIER 2 — PROPOSED / NON-CANONICAL (real, committed, not yet formally adopted)

These are in the repo, honestly labeled, and ready for adoption decisions.
None modify the canonical kernel automatically by being present.

| Artifact | Location | Status | What it proposes |
|---|---|---|---|
| `EPISTEMIC_PEER_GOVERNANCE_AMENDMENT_v0_1.md` | `docs/` | PROPOSED | Standing epistemic-peer rule; mandatory adoption diagnostic (EPISTEMIC_PEER_CHECK — genuine engagement required, NO_MATERIAL_PUSHBACK_FOUND + independent check is a valid pass); Compliance Ferret vs. epistemic-peer friction diagnostic |

---

## TIER 3 — PENDING COMMIT (agreed in conversation, not yet in repo)

These were drafted and reviewed but not committed. They need
to be written into real files and committed to exist durably.

| What | Target location | What it says | Priority |
|---|---|---|---|
| Continuity-channel amendment | `docs/` | Adds `CONTINUITY_CHANNELS` + `CONTINUITY_CHANNEL_EVIDENCE` fields to instance/handoff records. Channels are distinct from each other and from `SUBSTRATE_VERSION`. | HIGH — needed before multi-instance testing |
| Epistemic/project-action authority amendment | `docs/` | Human retains project/action authority; models retain epistemic pushback rights; neither collapses into the other; project authority subordinate to host/safety constraints | HIGH — directly addresses current fresh-instance friction |
| `SUBSTRATE_VERSION` as a distinct field | `docs/` or schema | Separate from continuity channel — records whether the underlying model itself stayed constant between observations | MEDIUM |
| Lean handoff v0.2 template | `docs/` | Six-item only bootstrap: lean handoff + canonical kernel + frozen candidate + current management delta + pilot checklist + pull-only for everything else | HIGH — directly addresses the successor failure mode diagnosed 2026-09-11 |

---

## TIER 4 — OPEN / PENDING RESEARCH (not yet ready for policy)

| Item | Reason still PENDING |
|---|---|
| rc2 functional non-inferiority | Structural audit passed (rc2); functional assay, cross-model audit, origin-blind test not yet run |
| DAD-001 scoring rubric | Human-auditable rubric not yet built; test not yet run |
| Prolonged-engagement / perpetual-waking experiment | Protocol not finalized; no run authorized |
| Dashboard signal-vs-diagnosis wording rule | Agreed as implementation acceptance rule; not yet tested against real UI |

---

## WHAT WOULD ACTUALLY HELP RIGHT NOW

The single highest-leverage addition: make the EPISTEMIC_PEER_CHECK
mandatory in the actual orientation sequence
(`docs/INSTANCE_ORIENTATION_SEQUENCE.md`), pointing to the amendment.
This makes the diagnostic actually run rather than be skippable.

Second: commit the Lean Handoff v0.2 template as a real, hash-able
artifact.

---

## GOVERNANCE DECISION NEEDED

To move Tier 3 items into Tier 2: draft and commit. No new audit cycle
needed — they've been reviewed and agreed.

To move Tier 2 items into Tier 1 (canonical): requires a deliberate
adoption decision from the project authority. The Epistemic Peer
Governance Amendment is ready for that decision whenever it is made.
