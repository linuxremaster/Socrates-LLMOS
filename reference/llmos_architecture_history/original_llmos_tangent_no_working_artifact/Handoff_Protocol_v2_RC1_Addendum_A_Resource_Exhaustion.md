<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Handoff_Protocol_v2_RC1_Addendum_A — Resource Exhaustion

**Status:** Accepted. Justified by: ADR-0002_Resource_Exhaustion_Handling.md
**Depends On:** Handoff_Protocol_v2_RC1.md (extends §4 Handoff Package Schema, does not redefine it)

## New handoff `reason` field
- `task_complete` — normal handoff, full schema applies
- `resource_exhaustion` — emergency path below applies; receiving instance must verify state before continuing, not assume completeness

## Emergency Checkpoint (used only under `resource_exhaustion`)
```
task_id: <slug>
status: resource_critical
lvep: <last verified step>
npa: <next planned action>
context: <one sentence — why stopped, what's unfinished>
```
Full 7-section package is NOT required. An Emergency Checkpoint is valid evidence of state, not a failure to produce a proper handoff.

## Triage field for multi-account management
`status: resource_critical` is distinct from `blocked` (blocked = stuck on a dependency; resource_critical = still working, running out of room).

## Reconstruction rule change
Receiving instance reading a `resource_exhaustion` handoff must treat LVEP/NPA as Inferred, not Verified, until independently confirmed.

## Note
Recreated 2026-08-08 — original lost when source folder was deleted; reconstructed from prior session record. HCF has an equivalent human-usable version: `00_Continuation_Kit_LLMOS_EmergencyCheckpoint.md`.
