<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Execution Boundary Updates

**Not an alert system.** Nothing here runs on its own. This is a log,
populated only when someone actually checks and finds something worth
recording — a session, a human, verifying `WHAT_THIS_IS_BUILT_ON.md`'s
provider policies against their current primary source, the same way
the RSP v3.1→v3.4 staleness was caught on 2026-08-16.

## Why this exists

The kernel's Execution Boundary means host-level trained model
behavior always outranks kernel text — the kernel instructs, it can't
enforce. If a provider's training or safety posture changes materially
(via corporate decision or regulatory mandate), the kernel's
instructions don't get overridden so much as they stop landing on
anything still disposed to follow them. Nothing in this repo can
detect that on its own. This log exists so that when it *is* checked,
the finding survives instead of evaporating.

## How to log a real entry

Use `llmos log-boundary-update` (see `llmos_toolkit/plugins/behavior_log`)
— it appends a structured record here and to `growth_ledger.jsonl`.
Only log something actually checked against a primary source, not
something merely heard about.

## Log

- **2026-08-16** [anthropic] Responsible Scaling Policy revised from v3.1 to v3.4 (effective 2026-07-08), found stale in WHAT_THIS_IS_BUILT_ON.md, corrected same day (verified against primary source, source: https://www.anthropic.com/rsp-updates)

**End Execution Boundary Updates**
