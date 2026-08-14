<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# ADR-0002_Resource_Exhaustion_Handling.md

**ADR ID:** ADR-0002
**Title:** Resource Exhaustion Handling for Handoff Protocol
**Status:** Accepted
**Depends On:** 01_LLMOS_Core_Runtime.md, Handoff_Protocol_v2_RC1.md, ADR-0001_Canonical_Specification_Governance.md

## Context
Free-tier accounts (multiple concurrent, mixed Claude/ChatGPT) do not expose real quota. Resource exhaustion is discovered at the moment it happens, not predicted. Handoff_Protocol_v2_RC1 §6 assumes reconstruction begins from a completed package — it does not address a package built under time/resource pressure, possibly incomplete.

## Problem Statement
Without an exhaustion-specific path, an instance hitting a limit either produces no handoff at all, or attempts a full 7-section package it may not have room to finish — both risk an empty or wrong-file reconstruction downstream.

## Decision
Add a Resource Exhaustion Addendum to the Handoff Protocol (separate file — see Handoff_Protocol_v2_RC1_Addendum_A_Resource_Exhaustion.md). Two mechanisms:
1. **Emergency Checkpoint** — minimal handoff variant (task_id, LVEP, NPA, one context line), writable in a single message.
2. **`status: resource_critical`** field, distinct from `blocked`, for triage across multiple accounts.

## Evidence
Verified: prior wrong-file reconstruction failure (ChatGPT relay incident). Inferred: multiple concurrent free-tier accounts increases exhaustion-during-task frequency vs. one paid instance. Assumed: message-count/session-time heuristics are usable proxies for quota, since no direct signal exists.

## Note on this document
Recreated 2026-08-08 — the original was lost when its source folder was deleted. Content reconstructed from prior session record, not re-derived from scratch.
