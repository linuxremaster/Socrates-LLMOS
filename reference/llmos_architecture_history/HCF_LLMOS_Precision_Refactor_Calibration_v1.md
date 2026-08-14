<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# HCF / LLMOS Precision Refactor Calibration

**Status:** Proposed / Pending Claude Consensus  
**Purpose:** Controlled drift audit and precision-refactor plan before changing canonical files.

## Method

**Drift → Ownership → Scope → Preservation calibration** was performed before proposing changes.

The calibration sequence is:

1. **Drift** — identify discrepancies between current artifacts and established behavior.
2. **Ownership** — determine which component owns each rule or responsibility.
3. **Scope** — separate legitimate refactor targets from deferred or unauthorized changes.
4. **Preservation** — protect verified behavior, evidence status, authority boundaries, and established decisions before optimizing wording or structure.

Findings are separated from inference. Unresolved authority questions remain **Unknown** rather than being resolved by assumption. This calibration phase does **not** authorize modification of canonical artifacts.


## 1. Baseline

The current experimental fork already establishes:
- host instructions remain authoritative;
- adoption means methodology application, not runtime takeover;
- literal execution is claimed only when an actual mechanism exists;
- capability states remain distinct;
- external model output is observation, not verification;
- the Adapter translates the Kernel rather than redefining it.

## 2. Drift Findings

### D1 — Version/reference drift
**Severity: High**

Current artifacts contain inconsistent version references: the Adapter/single-file package and Kernel copies do not consistently identify the same Kernel version.

**Action:** establish one authoritative version pair before release. Do not normalize by assumption.

### D2 — Duplicate boundary language
**Severity: Medium**

Host Authority, Methodology Adoption, capability, and self-execution distinctions appear in both Adapter and Kernel.

**Action:** retain a concise Adapter boundary for cold-start use; keep canonical detailed definitions in the Kernel; remove unnecessary duplicate normative text.

### D3 — Compatibility sequence ownership
**Severity: Low / verify**

The Adapter explicitly delegates the canonical compatibility sequence to the Kernel and says it should not duplicate it.

**Action:** preserve this ownership and verify the Kernel section reference after numbering changes.

### D4 — Single-file synchronization drift
**Severity: High**

The single-file package embeds copies of the Adapter and Kernel.

**Action:** treat it as a generated test artifact, never as a second canonical source.

### D5 — “Self-directing” ambiguity
**Severity: Medium**

The package correctly says Markdown does not literally execute itself, but “self-directing” can still be interpreted too strongly.

**Action:** define it once as ordered procedural guidance for a host LLM and use that meaning consistently.

### D6 — Output-integrity terminology density
**Severity: Medium**

The output pipeline is substantively strong but terminology-heavy.

**Action:** optimize representation only; preserve MUST-SURVIVE, evidence/provenance, reconstruction, measurement, and stop controls.

## 3. Component Ownership

```text
HOST AUTHORITY
      │
      ▼
COMPATIBILITY ADAPTER
  host capability + boundary translation
      │
      ▼
KERNEL
  canonical methodology + resolution rules
      │
      ▼
GLOBAL CHECK
  substantive-output verification
      │
      ▼
TASK OUTPUT
```

**Adapter owns:** host boundary, capability discovery, adaptation mode, translation, availability, conflict classification.

**Kernel owns:** canonical methodology, evidence model, objective/dependency discipline, compatibility resolution, promotion rules, output-integrity rules, research/audit rules.

**GLOBAL CHECK owns:** final substantive-output review, semantic preservation, evidence/provenance checks, execution/continuation integrity.

No component should redefine another component's canonical rules.

## 4. Precision Refactor Rules

1. Preserve behavior before wording.
2. Preserve evidence status before compression.
3. Preserve authority boundaries before convenience.
4. Remove duplicate definitions only after ownership is explicit.
5. Never resolve version discrepancies by assumption.
6. Do not promote external-model proposals without authorization.
7. Do not reopen deferred design questions.
8. Keep the single-file package generated from canonical sources.
9. Check every changed cross-reference.
10. Stop after one controlled refactor pass.

## 5. Scope

**In scope:** version/reference reconciliation, terminology normalization, component ownership, duplicate-definition reduction, single-file generation relationship, cross-reference verification, first-contact clarity.

**Out of scope:** methodology redesign, G-017 redesign, paused architecture proposals, Host Authority Boundary changes, safety/evidence weakening, deferred governance questions.

## 6. Claude Consensus Relay

Review this as an observation-based refactor proposal, not authorization.

1. Confirm/reject D1–D6.
2. Identify additional drift directly supported by the supplied files.
3. Propose exact wording/ownership changes only where justified.
4. Preserve scope boundaries.
5. Do not modify canonical artifacts yet.
6. Return a compact reconciliation for one implementation pass.

## 7. Evidence Status

**Verified:** Current Adapter and Kernel contain the cited authority, capability, evidence, and compatibility mechanisms.

**Verified:** The single-file package embeds component copies.

**Inferred:** Version/reference inconsistency creates synchronization risk.

**Unknown:** Which version pair is intended to become canonical.

**Unknown:** Which historical duplicates should be archived or retired.

## 8. Release Gate

Do not label the refactor Canonical, Final, or Frozen until version authority is resolved, Claude consensus is complete, changes are authorized, canonical files are updated, cross-references are checked, the single-file package is regenerated, and GLOBAL CHECK passes.
