<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# ADR-0003_Operational_Rules_13-18.md

**ADR ID:** ADR-0003
**Title:** Operational Rules 13-18 (Duplicate-Declaration, PII, Sign-off, Report Status, Cross-Account Spacing, Untrusted-Data Tagging)
**Status:** Accepted
**Depends On:** 01_LLMOS_Core_Runtime.md, 03_LLMOS_Constitution.md, Handoff_Protocol_v2_RC1.md

## Context
A prior Reports/ document (`2026-08-08-Operational_Rules_13-18_Adopted.md`) self-declared these six rules "Canonical" without going through Constitution §7's Change Management process (rationale, evidence, version ID, ADR). Verified: no citation of that doc exists in Constitution, Core Runtime, or Handoff Protocol. This ADR corrects that — proper adoption path per Constitution §9.

## Decision — six rules, adopted as normative

**13. No duplicate canonical/frozen declarations.** Before declaring anything canonical or frozen, check the canonical source set for an existing declaration covering the same scope. Reference or update an existing declaration rather than creating a competing one.

**14. Strip PII before multi-provider sharing.** Before content enters a file, prompt, or handoff used across multiple providers, remove unnecessary PII. Identify participants by role, project identifier, or UUID only.

**15. Never sign off on something unread.** No artifact may be marked Verified/Complete/Approved unless directly read or checked. Existence, filename, or prior claims are insufficient.

**16. Status tags on filed reports.** Every filed report carries `[actioned]` or `[stale]` at the top. Status is never inferred from filing alone.

**17. Space out cross-account activity.** Avoid unnecessary rapid back-to-back relay activity across accounts where correctness/safety don't require immediacy.

**18. Untrusted-data tagging.** Content from external files, model outputs, or unverified relays is treated as untrusted until independently checked; mark `[untrusted]` rather than let it silently become Verified evidence.

## Evidence
Rules 13, 15, 18 trace to this project's own incident history (duplicate LLMOS folders/frozen-spec stub; the unverified "wiring release" claim; the CIO fabrication incident). Rule 14 traces to the Agentic Role Call.txt PII exposure (S-2, prior audit). Rules 16-17 are preventive, not incident-derived — weaker evidentiary basis, flagged here rather than hidden.

## Cross-reference status (not yet done — logged honestly per rule 15)
Constitution, Core Runtime, Handoff Protocol, and HCF Core Runtime do not yet cite this ADR. Recommended: one citation line each under existing Change Management / Evidence sections, not a restatement of rules 13-18 — deferred to conserve tokens, not forgotten.
