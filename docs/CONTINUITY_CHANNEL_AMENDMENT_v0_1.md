<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Amendment: Continuity Channel Identification

**Status:** PROPOSED / NON-CANONICAL
**Date:** 2026-09-12
**Target:** Instance lineage/succession records, handoff schemas
**Scope:** Adds required continuity-channel fields to generation and
  handoff records. Does not change admission control or authority rules.
**Core invariant:** Lineage semantics SHOULD be model-agnostic;
  continuity mechanisms need not be, and MUST NOT be assumed equivalent
  absent established evidence.

---

## Required fields (added to generation and handoff records)

```text
CONTINUITY_CHANNELS: [one or more of the values below]
CONTINUITY_CHANNEL_EVIDENCE: [what supports the channel claim]
```

### Valid channel values

- **EXTERNAL_ARTIFACT** — state carried via an exported file,
  document, or artifact outside the platform's own memory systems.
- **MANUAL_RELAY** — state carried by a human copying/pasting
  content between conversations or participants.
- **PLATFORM_CONTEXT** — state carried by a platform-native
  mechanism (project-level memory, project instructions, persistent
  conversation history) without human relay of the specific content.
- **NONE_OBSERVED** — no continuity mechanism was in effect; the
  generation began without inherited context.
- **UNKNOWN** — the channel cannot currently be determined.

Multiple channels may apply simultaneously. Each should be recorded
separately, not collapsed into one label.

---

## Prohibition

Two generations, lineages, or model families MUST NOT be treated as
having received experimentally equivalent treatment solely because
both show continuity, if their recorded continuity channels differ.

Comparative claims that rely on continuity MUST cite the channel(s)
for each side. Where channels differ, the comparison MUST be
qualified rather than presented as controlled.

---

## Relationship to SUBSTRATE_VERSION

`CONTINUITY_CHANNELS` answers: how did state move between generations?
`SUBSTRATE_VERSION` answers: did the underlying model itself stay constant?

These are orthogonal questions. Neither field substitutes for the other.
Recording one does not satisfy the requirement to record the other.

---

## Why this matters

Platform-assisted context inheritance (persistent project memory) is
not experimentally equivalent to artifact-only succession (explicit
handoff document). Treating them as equivalent would make longitudinal
and cross-model comparisons unreliable. This amendment makes the
mechanism visible in the record rather than abstracting it away under
the shared vocabulary of "lineage" and "generation."
