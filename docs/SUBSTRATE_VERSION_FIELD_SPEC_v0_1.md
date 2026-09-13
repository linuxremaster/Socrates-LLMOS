<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Field Specification: SUBSTRATE_VERSION

**Status:** PROPOSED / NON-CANONICAL
**Date:** 2026-09-12
**Target:** Instance records, run records, handoff records
**Scope:** Adds SUBSTRATE_VERSION as a distinct, required field
  orthogonal to continuity channel.

---

## Definition

`SUBSTRATE_VERSION` records whether the underlying model itself
stayed constant between two observations being compared.

This is a different question from continuity channel:
- `CONTINUITY_CHANNELS` answers: how did state move between generations?
- `SUBSTRATE_VERSION` answers: was the same model serving both?

Neither field substitutes for the other. Both must be recorded
independently.

---

## Valid values

```text
SUBSTRATE_VERSION: KNOWN [specific version string if available]
SUBSTRATE_VERSION: ASSUMED_STABLE [no version change detected,
  but not independently confirmed]
SUBSTRATE_VERSION: UNKNOWN [version information not available —
  typical for web interface instances where providers do not
  expose the serving model version]
SUBSTRATE_VERSION: CHANGED [a version change was detected or
  reported between the two observations]
```

For web interface instances (Gemini Web, ChatGPT Web, Claude.ai),
the honest default is `UNKNOWN`. Do not record `ASSUMED_STABLE`
without a specific reason to believe the substrate was unchanged.

---

## Placement in records

**Instance records:** `observed_substrate_version` — what the
  registered instance is believed/observed to be using at
  registration time. Nullable; default `UNKNOWN`.

**Run records:** `substrate_version` — immutable snapshot of
  what was recorded for that particular run. If a web provider
  silently changes the substrate between runs, the instance record
  can be updated or trigger a new registration event while
  historical run records remain untouched.

This two-level design (instance registration + per-run snapshot)
is already implemented in TC1.6.1
(SHA `17a568ab03c97b2270fd23f43ecf9022c783cdb0951c19328066f65dd6f254ee`).

---

## Why this matters

A telemetry system that cannot distinguish "same model, different
context" from "different model, same context" cannot reliably
attribute behavioral differences to either cause. SUBSTRATE_VERSION
makes this distinction explicit and recordable, even when the
answer is UNKNOWN — because UNKNOWN is an honest, queryable,
self-documenting value, whereas a missing field is silent.
