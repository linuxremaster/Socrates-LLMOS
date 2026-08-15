<!--
ARCHIVED HISTORICAL SPECIFICATION — NOT CURRENT IMPLEMENTATION.
This document describes a superseded or experimental LLMOS architecture.
It does not describe the current kernel's execution boundary and must
not be treated as a current authority, runtime implementation, or
capability declaration. See docs/LLMOS_SCOPE_AND_BOUNDARIES.md for the
current, authoritative distinction between the kernel (methodology) and
the toolkit (executable software).
-->
<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# LLMOS Architecture Update v1.1 (Review Draft)

## Status

Architecture refinement based on: - Boot Architecture specification -
Project State Manifest specification - Procedure Manifest
specification - Screenshot architectural proposals

## Canonical Separation

### Deployment Layer

``` text
User
  │
Termux Relay / Coordinator
  │
Provider Adapters
├─ Claude
├─ ChatGPT
└─ Gemini
  │
Shared Workspace
```

Responsibilities: - Session routing - Artifact synchronization -
Manifest exchange - Provider abstraction

### LLMOS Runtime

``` text
Initiation Prompt
      │
Bootloader
      │
Kernel
      │
Manifest Specifications
      │
Current Project Manifests
      │
Evidence Package
      │
Reconstruction Engine
      │
Execution Engine
      │
Output Validation
      │
Checkpoint & Handoff
```

## Architectural Decisions

-   Deployment remains outside the runtime.
-   Kernel remains provider-independent.
-   Manifest Specifications define schemas only.
-   Project Manifests are generated runtime state.
-   Evidence is immutable input.
-   Reconstruction identifies the LVEP.
-   Execution resumes from the earliest unresolved dependency.
-   Checkpoint regenerates manifests and successor package.

## Remaining Deliverables

1.  LLMOS Runtime Blueprint v1.0
2.  LLMOS Bootloader Specification
3.  LLMOS Kernel Specification
4.  Termux Relay Specification

## Completion Assessment

Estimated architectural completeness: 90--95%.

Primary remaining work is implementation and specification refinement
rather than additional architectural expansion.
