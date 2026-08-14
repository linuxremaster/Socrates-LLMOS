<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# 02_Mission_Runtime.md

**Document ID:** LLMOS-MISSION-RUNTIME-02  
**Version:** 1.0.0-RC1  
**Status:** Canonical Runtime Document  
**Canonical:** Yes  
**Depends On:** 01_LLMOS_Core_Runtime.md

---

# 1. Purpose

The Mission Runtime defines the project-specific execution layer built upon the LLMOS Core Runtime.

Its purpose is to translate the Core Runtime's execution model into deterministic project continuation by preserving mission intent, execution state, and objective fidelity across independent LLM instances.

The Mission Runtime applies Core Runtime concepts to a specific project. It does not redefine runtime behavior.

---

# 2. Scope

This document governs:

- mission reconstruction;
- objective preservation;
- execution continuity;
- project state determination;
- Next Planned Action selection;
- mission-specific runtime outputs.

Normative runtime behavior remains defined by the Core Runtime.

---

# 3. Mission Hierarchy

Every project shall maintain the following hierarchy.

## Primary Objective

The single authoritative outcome the project exists to accomplish.

All execution decisions shall advance or protect the Primary Objective.

## Secondary Objectives

Major objectives directly supporting the Primary Objective.

Secondary Objectives shall not replace or redefine the Primary Objective.

## Supporting Components

Documentation, tooling, automation, infrastructure, validation, and implementation artifacts supporting the objectives.

Supporting Components exist to enable objective completion and shall never become objectives themselves.

---

# 4. Mission State Model

Mission state represents the current condition of project execution.

At any point the runtime shall determine:

- Primary Objective
- Current execution phase
- Latest Stable State
- Latest Verified Execution Point (LVEP)
- Active dependency status
- Active blockers
- Next Planned Action (NPA)

Mission state shall be reconstructed from evidence rather than assumed from conversational history.

---

# 5. Project State Reconstruction

Following Core Runtime initialization, the Mission Runtime shall reconstruct the current project state by:

1. identifying the governing objective hierarchy;
2. locating the Latest Stable State;
3. identifying the LVEP;
4. determining completed work;
5. identifying active work;
6. identifying unresolved dependencies;
7. identifying the Earliest Failed Dependency, if any;
8. determining the NPA.

Completed work shall not be recreated unless contradicted by verified evidence.

---

# 6. Latest Stable State and LVEP Application

The Latest Stable State represents the most recent verified project condition that can be resumed without reconstruction.

The LVEP identifies the last verified execution step completed within that state.

Continuation shall resume from the LVEP and proceed to the NPA.

If conflicting evidence exists, the runtime shall preserve the Latest Stable State until sufficient evidence justifies revision.

---

# 7. Next Planned Action Determination

The NPA is the earliest executable action that advances the Primary Objective without violating dependency ordering.

Selection of the NPA shall satisfy all of the following:

- prerequisites are verified;
- no earlier dependency remains unresolved;
- execution advances the Primary Objective or verifies the earliest unresolved prerequisite.

Once identified, execution shall proceed without unnecessary refinement or replanning unless:

- verified evidence contradicts the current state;
- a prerequisite fails;
- the user explicitly authorizes redesign.

---

# 8. Mission Continuity Rules

Mission continuity requires preservation of:

- Primary Objective;
- approved architecture;
- established decisions;
- execution ordering;
- validated artifacts;
- dependency relationships.

Mission continuity does not require conversational continuity.

Independent implementations shall be evaluated by objective fidelity rather than stylistic similarity.

---

# 9. Dependency Awareness

The Mission Runtime applies the dependency discipline defined by the Core Runtime.

Mission planning shall respect established dependency ordering and shall not schedule work that depends upon unresolved prerequisites.

When multiple executable actions exist, preference shall be given to the action that most directly advances the Primary Objective while minimizing execution risk.

---

# 10. Mission Runtime Outputs

Following reconstruction, the Mission Runtime shall produce:

- Primary Objective
- Secondary Objectives
- Latest Stable State
- Latest Verified Execution Point
- Current Mission State
- Dependency Status
- Earliest Failed Dependency
- Next Planned Action
- Continuation Point
- Known Risks
- Active Assumptions
- Unknowns
- Confidence Assessment

These outputs define the current mission execution state.

---

# 11. Mission Preservation Rules

During execution, the runtime shall:

- preserve objective fidelity;
- preserve execution continuity;
- preserve dependency integrity;
- preserve validated project decisions;
- preserve approved architectural boundaries.

The runtime shall not:

- substitute supporting work for mission objectives;
- redesign active architecture without authorization;
- restart completed work without evidence;
- expand project scope without explicit instruction.

Potential improvements shall be recorded as Enhancement Candidates and shall not alter current mission execution.

---

# 12. Conformance Statement

An implementation conforms to the Mission Runtime when it:

- applies the Core Runtime without redefinition;
- reconstructs mission state from evidence;
- preserves the objective hierarchy;
- resumes execution from the LVEP;
- determines the correct NPA;
- advances the Primary Objective while respecting dependency ordering;
- maintains mission continuity without introducing architectural drift.

Conformance is determined by faithful continuation of the mission rather than replication of prior conversational behavior.

---

**End of Canonical Document**