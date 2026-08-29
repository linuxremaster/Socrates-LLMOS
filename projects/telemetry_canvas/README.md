<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Socrates Telemetry Canvas

**Status: active, standalone project deliverable. Non-canonical.**

A single-file, offline-first HTML/JS console for capturing telemetry
from web-based (non-API) LLM instances by hand — structured event
logging, hash-chained tamper evidence, deterministic surface
detection, and evidence/provenance/authority tagging, without any
network calls.

## What "active project" means here, precisely

This directory holds the same status as `projects/depolarize` and
`projects/relay_console` — a real, standalone deliverable that gets
maintained and versioned in its own right.

**It does not mean the Canvas is integrated into the `llmos_toolkit`
runtime.** There is no automated data path from a Canvas export into
`growth_ledger.jsonl` or `behavior_log`. Moving this out of `reference/`
(archived, non-maintained) and into `projects/` (active, maintained)
is an organizational status change, not a runtime integration — see
`docs/TELEMETRY_CANVAS_LLMOS_RELATIONSHIP.md` (adopted 2026-08-29) for
the full, current, correct description of how the Canvas and the LLMOS
runtime actually relate: the Canvas is a human-clocked bridge, not a
component of the runtime, and automated ingestion remains an explicit,
separate, `PENDING` future decision.

## Files

- `Socrates_Telemetry_Canvas_v0.9.2-alpha.html` — the active version.
  Open directly in a browser; no install, no build step, no server.
- `CHANGELOG.md` — real version history, including the v0.10.0
  abandonment decision (a near-total accidental rewrite that dropped
  hash-chaining, self-tests, and surface detection; not the successor
  to v0.9.0) and the v0.9.1 → v0.9.2 fixes (prompt-numbering
  stability, model-agnostic generalization, storage migration).
- `archive/` — real, preserved prior/abandoned versions, kept for
  direct diffing rather than trusted-by-description. Not deleted.

## Real, tested properties (not just claimed)

Every version-to-version change here has been verified by actually
executing the code — a Node harness with mocked browser APIs, real
hash-chain append/verify/tamper-detection, real self-test runs, real
kernel load/swap tests — not by code review alone. See `CHANGELOG.md`
for what was specifically tested at each version.
