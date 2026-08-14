<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Handoff_Protocol_v2_RC1.md

**Document ID:** LLMOS-HANDOFF-PROTOCOL-V2-RC1  
**Version:** 2.0.0-RC1  
**Status:** Canonical Protocol Document  
**Canonical:** Yes  
**Depends On:**  
- 01_LLMOS_Core_Runtime.md  
- 02_Mission_Runtime.md

---

# 1. Purpose

The Handoff Protocol defines the deterministic transfer procedure between independent LLM instances.

Its purpose is to enable a newly initialized instance to reconstruct the current project state from a structured evidence package while preserving objective fidelity, execution continuity, and architectural integrity.

The Handoff Protocol consumes the Core Runtime and Mission Runtime. It does not redefine their responsibilities.

---

# 2. Scope

This document governs:

- construction of the handoff package;
- transfer of project state;
- application of the Evidence Model during reconstruction;
- validation of reconstructed state;
- failure handling during initialization.

Runtime behavior remains governed by the Core Runtime.

Mission behavior remains governed by the Mission Runtime.

---

# 3. Handoff Inputs

A conforming handoff package shall contain only information necessary for deterministic continuation.

Required inputs include:

## Runtime Documents

- 01_LLMOS_Core_Runtime.md
- 02_Mission_Runtime.md

## Project Documents

Current canonical specifications, protocols, architecture documents, ADRs, manifests, and other approved artifacts required for continuation.

## Execution State

The package shall identify:

- Latest Stable State
- Latest Verified Execution Point (LVEP)
- Next Planned Action (NPA)

## Supporting Evidence

Only evidence necessary to reconstruct current execution state shall be included.

Historical discussion shall not be transferred unless required to explain a verified project decision.

---

# 4. Handoff Package Schema

Every handoff package shall include the following sections.

## A. Mission Summary

A concise description of the current Primary Objective and active Secondary Objectives.

## B. Project State

Current execution phase.

Completed work.

Active work.

Blocked work.

Pending work.

## C. Execution Continuity

Latest Stable State.

LVEP.

NPA.

Continuation Point.

## D. Dependency Status

Current dependency status.

Earliest Failed Dependency, if applicable.

Known execution blockers.

## E. Evidence Register

Verified Facts.

Inferred Conclusions.

Active Assumptions.

Unknowns.

Evidence classifications shall reference the Core Runtime Evidence Model.

## F. Active Risks

Current execution risks affecting continuation.

## G. Canonical Artifact List

Only currently authoritative documents shall be identified.

Superseded artifacts shall not appear as canonical.

---

# 5. Evidence Model Application

The handoff shall preserve the evidence classifications defined by the Core Runtime.

Every transferred statement shall remain classified as one of:

- Verified
- Inferred
- Assumed
- Unknown

The protocol shall not promote an assumption to verified status during transfer.

If conflicting evidence exists, both the conflict and supporting sources shall be transferred without attempting architectural resolution.

---

# 6. Reconstruction Procedure

The receiving instance shall:

1. Read the Core Runtime.
2. Read the Mission Runtime.
3. Read the Handoff Package.
4. Load referenced project artifacts.
5. Apply the Core Runtime Evidence Model.
6. Reconstruct mission state.
7. Verify the Latest Stable State.
8. Verify the LVEP.
9. Verify dependency status.
10. Determine the NPA.
11. Continue execution.

Reconstruction terminates once the NPA has been identified with sufficient evidence under the governing runtime.

The receiving instance shall not redesign architecture during reconstruction.

---

# 7. Validation Procedure

Following reconstruction, the receiving instance shall verify that:

- the Primary Objective matches the supplied mission;
- the reconstructed Latest Stable State is supported by evidence;
- the LVEP is internally consistent;
- dependency ordering is preserved;
- the NPA follows dependency discipline;
- evidence classifications remain unchanged;
- no unsupported assumptions have become verified facts.

If a discrepancy is detected, it shall be classified as either:

- Implementation Conformance Issue; or
- Specification Ambiguity.

When classification is uncertain, the default classification shall be **Specification Ambiguity** unless an explicit requirement in the governing specifications establishes a single interpretation.

---

# 8. Runtime Outputs

Following successful reconstruction, the receiving instance shall produce:

- Primary Objective
- Latest Stable State
- Latest Verified Execution Point
- Current Mission State
- Dependency Status
- Earliest Failed Dependency
- Next Planned Action
- Continuation Point
- Verified Facts
- Active Assumptions
- Unknowns
- Confidence Assessment
- Known Risks

These outputs become the current operational state for continued execution.

---

# 9. Failure Handling

If reconstruction cannot complete, the receiving instance shall identify exactly one blocking prerequisite.

Failure responses shall distinguish between:

## Missing Evidence

Required evidence is unavailable.

## Specification Ambiguity

Multiple reasonable interpretations exist.

## Dependency Failure

A prerequisite prevents continuation.

## Package Integrity Failure

The handoff package is incomplete, internally inconsistent, or references unavailable canonical artifacts.

The protocol shall not compensate for missing evidence through speculation.

Execution resumes only after the blocking prerequisite has been resolved or explicitly overridden by the user.

---

# 10. Conformance Statement

An implementation conforms to Handoff Protocol v2 RC1 when it:

- consumes the Core Runtime and Mission Runtime without redefining them;
- reconstructs project state from the supplied handoff package;
- preserves evidence classifications throughout reconstruction;
- preserves execution continuity from the Latest Stable State through the LVEP to the NPA;
- identifies blocking prerequisites without speculation;
- produces the required runtime outputs; and
- resumes execution without introducing architectural drift.

Conformance is determined by deterministic reconstruction from evidence rather than conversational similarity or implementation style.

---

**End of Canonical Document**