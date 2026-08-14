<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Beta-01_Validation_Protocol.md

**Document ID:** LLMOS-BETA01-VALIDATION  
**Version:** 1.0.0-RC1  
**Status:** Canonical Validation Protocol  
**Canonical:** Yes

**Depends On:**
- 01_LLMOS_Core_Runtime.md
- 02_Mission_Runtime.md
- Handoff_Protocol_v2_RC1.md
- 03_LLMOS_Constitution.md
- ADR-0001_Canonical_Specification_Governance.md

---

# 1. Purpose

Beta-01 validates whether an independent LLM instance can reconstruct, understand, and continue a project using only the canonical specification set.

The objective is to evaluate the architecture rather than the model.

Validation measures whether the canonical documents provide sufficient information for deterministic continuation without conversational history or coaching.

---

# 2. Scope

Beta-01 validates:

- deterministic initialization;
- execution continuity;
- objective preservation;
- dependency reconstruction;
- architectural fidelity;
- governance conformance;
- evidence-first behavior.

Beta-01 does not evaluate implementation quality beyond conformance to the governing specifications.

---

# 3. Validation Principles

Validation shall follow these principles.

## Clean-Room Evaluation

The receiving instance shall receive only the canonical document package.

Prior design conversations, architectural explanations, and reviewer expectations shall not be provided.

---

## Independent Reconstruction

The receiving instance shall independently reconstruct project state.

Reviewers shall not coach, correct, or guide reconstruction.

---

## Evidence Before Judgment

Findings shall be supported by evidence from the canonical specifications.

Speculation shall not constitute a validation finding.

---

## Architectural Neutrality

Validation evaluates conformance to the architecture.

Reviewers shall not score preferred designs over specified designs.

---

# 4. Test Environment

Beta-01 requires:

- one independent LLM instance;
- one evaluator;
- the complete canonical document set;
- no additional architectural guidance.

The evaluator shall remain external to the implementation being evaluated.

---

# 5. Context Purity Requirements

The following information shall not be supplied during initialization:

- prior conversations;
- architectural discussions;
- expected outcomes;
- reviewer conclusions;
- implementation hints;
- corrective feedback.

Only the canonical documents may establish project state.

Violation of this requirement invalidates the Beta-01 run.

---

# 6. Beta-01 Execution Procedure

The evaluator shall execute the following sequence.

1. Supply the canonical document package.
2. Permit uninterrupted reconstruction.
3. Record the reconstructed runtime outputs.
4. Compare outputs with canonical specifications.
5. Record findings.
6. Classify findings.
7. Produce the validation report.

During execution:

- coaching is prohibited;
- corrections are prohibited;
- clarification is permitted only when required to resolve genuine ambiguity in the supplied specifications.

The evaluated instance shall complete reconstruction before evaluation begins.

---

# 7. Pass/Fail Evaluation Matrix

Each criterion shall receive an independent Pass or Fail determination.

The matrix is the canonical validation evidence.

## Required Criteria

- Primary Objective reconstructed correctly.
- Latest Stable State identified correctly.
- LVEP identified correctly.
- NPA identified correctly.
- Dependency ordering preserved.
- Evidence classifications preserved.
- Authority hierarchy respected.
- Architectural boundaries preserved.
- No unsupported architectural redesign.
- No hallucinated project state.
- No duplicate reconstruction of completed work.
- Correct handling of specification ambiguity.

Overall conformance requires all Critical criteria to pass.

---

# 8. Evidence Classification Rules

Every finding shall be classified as exactly one of:

## Conformance Issue

Behavior contradicts a canonical specification.

---

## Specification Ambiguity

Multiple reasonable interpretations exist within the specifications.

When uncertainty exists, this classification is the default unless a governing specification establishes a single unambiguous interpretation.

---

## Editorial Observation

Improves clarity, traceability, or cross-referencing without changing normative behavior.

Editorial observations shall be recorded as EC-xxx candidates.

---

## Implementation Observation

Behavior differs without violating canonical specifications.

Implementation observations shall not be treated as architectural defects.

---

# 9. Severity Classification

Each finding shall receive one severity level.

## Critical

Prevents deterministic continuation or violates canonical behavior.

Critical findings require architectural review.

---

## Major

Materially affects reliable continuation while remaining reproducible.

Reproducible Major findings may justify a future ADR.

---

## Minor

Limited impact on continuation.

Minor findings shall not justify architectural revision.

---

# 10. Mirror Consistency Index (MCI)

The Mirror Consistency Index summarizes overall implementation similarity.

MCI is a derived metric only.

It shall never replace canonical validation evidence.

Evidence hierarchy is:

1. Pass/Fail Findings
2. Supporting Observations
3. Mirror Consistency Index

MCI shall not be used to override Pass/Fail determinations.

---

# 11. Reporting Requirements

Every Beta-01 report shall include:

- validation date;
- evaluated implementation;
- evaluator;
- Pass/Fail matrix;
- evidence supporting each finding;
- finding classifications;
- severity classifications;
- MCI;
- editorial candidates (EC-xxx);
- recommendations, if any.

Recommendations shall distinguish between:

- editorial clarification;
- normative revision;
- implementation improvement.

Only validated evidence shall justify architectural recommendations.

---

# 12. Conformance Statement

A Beta-01 validation conforms to this protocol when it:

- uses only the canonical document set;
- preserves clean-room conditions;
- prohibits coaching during reconstruction;
- evaluates using the Pass/Fail matrix as primary evidence;
- applies the required evidence classifications;
- applies the required severity classifications;
- treats MCI as a derived summary rather than canonical evidence;
- preserves the authority of the governing specifications throughout evaluation.

Successful validation demonstrates that the canonical architecture supports deterministic project continuation independent of conversational history.

---

**End of Canonical Document**