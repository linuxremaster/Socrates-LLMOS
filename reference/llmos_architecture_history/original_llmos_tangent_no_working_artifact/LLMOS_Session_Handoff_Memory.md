<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# LLMOS Session Handoff Memory

**Purpose:** Preserve continuity for the next chat instance.

## Current Objective

Finalize the LLMOS runtime architecture and begin producing
implementation artifacts rather than additional architectural redesign.

## Canonical Direction

-   Separate **Deployment Layer** from **LLMOS Runtime**.
-   Deployment includes: User, Termux Relay/Coordinator, provider
    adapters (Claude, ChatGPT, Gemini), shared workspace.
-   Runtime includes: Initiation Prompt → Bootloader → Kernel → Manifest
    Specifications → Project Manifests → Evidence Package →
    Reconstruction Engine → Execution Engine → Output Validation →
    Checkpoint & Handoff.

## Kernel Status

The kernel prompt has been expanded with rules for: - Objective
preservation - Evidence-first execution - Root-cause-first
troubleshooting - Artifact-first generation - Anti-parroting -
Attribution integrity - Refinement suppression - Deliverable-first
execution - Completion verification - Output integrity - Rule
precedence - Failure recovery - Scope control

Intent: reduce analysis/refinement loops and maximize tangible
artifacts.

## Architectural Conclusions

-   Runtime is provider-agnostic.
-   Termux relay is a deployment component, not part of the kernel.
-   Manifest Specifications define schemas.
-   Project/Procedure Manifests are generated runtime state.
-   Evidence is immutable input.
-   Reconstruction identifies LVEP.
-   Execution resumes from LVEP / earliest unresolved dependency.
-   Checkpoint produces successor package.

## Estimated State

Architecture: \~90--95% complete. Remaining work is
implementation/specification, not redesign.

## Highest-Priority Deliverables

1.  LLMOS Runtime Blueprint v1.0
2.  Bootloader Specification
3.  Kernel Specification
4.  Termux Relay Specification
5.  Interactive non-linear HTML blueprint

## Behavioral Expectations

-   Execute before discussing.
-   Produce downloadable artifacts by default.
-   Treat additional ideas as enhancement candidates unless requested.
-   Preserve attribution accurately.
