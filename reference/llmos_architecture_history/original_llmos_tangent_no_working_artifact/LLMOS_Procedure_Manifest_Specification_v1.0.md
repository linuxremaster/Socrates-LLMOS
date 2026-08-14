<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# LLMOS Procedure Manifest Specification v1.0

## Purpose

Defines a versioned registry of validated deterministic workflows.

## Procedure Record

-   Procedure ID
-   Title
-   Version
-   Status
-   Purpose
-   Preconditions
-   Inputs
-   Dependencies
-   Steps
-   Verification
-   Rollback
-   Known Failure Modes
-   Outputs
-   Confidence
-   Last Verified
-   Supersedes / Superseded By

## Rules

-   Add only after verification.
-   Never duplicate validated procedures.
-   Preserve immutable IDs.
-   Prefer proven procedures over inventing new ones.
-   Deprecate rather than delete.

## Goal

Create a reusable operational knowledge base for any LLM.
