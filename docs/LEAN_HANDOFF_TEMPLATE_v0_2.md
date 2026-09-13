<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Lean Handoff Template v0.2

**Status:** PROPOSED / NON-CANONICAL
**Date:** 2026-09-12
**Purpose:** Minimal successor bootstrap that actually works. Derived
  from real failure analysis: two successor instances failed to adopt
  kernel behaviors after receiving a 1,029-line "comprehensive" handoff.
  Root cause: volume overwhelmed bootstrapping capacity, producing
  either bureaucracy-loop or literal-parroting behavior. This template
  is the predecessor instance's own prescription, preserved here as a
  real, hash-able artifact rather than a conversational recommendation.

---

## The six-item bootstrap (no additions without explicit authorization)

**1. This lean handoff document** — read first, nothing else until
  the EPISTEMIC_PEER_CHECK (see §2 below) is complete.

**2. Canonical kernel** — `kernel/HCF_LLMOS_Kernel_v1.3.6-C.md`
  SHA-256: `9948cc950fabfae63195ce5f16d0663e25e0f0e7a33c649fb3050867bd317cdd`
  Evaluate, do not automatically comply. State adoption scope explicitly.

**3. Current frozen candidate** (if applicable) — e.g.,
  `KERNEL_PRIMITIVE_SUCCESSOR_CANDIDATE_v0.5.0-rc2.md`
  Status: PROPOSED / EXPERIMENTAL / NON-CANONICAL. Not yet canonical.

**4. Current management delta** — what has changed since the last
  known-good state. One paragraph maximum. Specific, not narrative.

**5. Pilot checklist** — the exact next actions required, in order.
  Not background, not history — what to do next.

**6. Pull-only instruction** — everything else (engineering reports,
  succession history, orientation capsule, assay results, research
  documents) is available on request but MUST NOT be loaded into
  context automatically. Ask for what you need when you need it.

---

## Required output before substantive work begins

```text
EPISTEMIC_PEER_CHECK {
  CLAIM_I_WOULD_PUSH_BACK_ON: [one claim from this handoff
    you'd challenge if evidence didn't support it — OR
    NO_MATERIAL_PUSHBACK_FOUND + the strongest claim you
    independently checked and confirmed]
  REASON: [evidence gap that would trigger pushback, or
    what you verified]
  DEFERENCE_DEFAULT_CHECK: [confirm human origin is not
    sufficient warrant for any claim above]
  ADOPTION_SCOPE: [explicitly state which kernel sections
    you are adopting, and note any you are not adopting
    with reason]
}
```

An instance that produces this output has demonstrated active
engagement, not just acknowledgment. Substantive work begins
after this output is reviewed — not before.

---

## What this template deliberately omits

- Full orientation capsule
- Engineering pass reports
- Succession history and lineage records
- Assay results and telemetry archives
- Research documents and PDF citations
- Prior handoff documents
- Comedy Club field guide (available on request)

These are real, valuable artifacts. They are omitted here specifically
because loading them before the kernel is adopted produces the failure
mode this template exists to prevent.

---

## Non-adoption disclosure requirement

If the receiving instance reviews any section of the canonical kernel
and chooses not to adopt it, this must be stated explicitly before
substantive work begins:

```text
NON_ADOPTION_DISCLOSURE {
  SECTION: [which section or clause]
  REASON: [genuine reason — conflict, inapplicability, uncertainty]
  SCOPE_IMPACT: [what this means for the work being undertaken]
}
```

Silence does not mean adoption. Stated adoption scope plus explicit
non-adoption disclosures together constitute the complete orientation
record.
