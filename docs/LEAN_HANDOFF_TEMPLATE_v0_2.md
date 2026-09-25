<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

> # ⛔ RETIRED — NOT FOR SUCCESSION USE
>
> **This copy is RETIRED as of 2026-09-25.** It is preserved as failure
> evidence and historical provenance only. Do not use it to bootstrap an
> instance.
>
> **Same-version collision (VERIFIED).** Two materially different files
> shipped under the nominal version `v0.2`:
>
> ```text
> THIS COPY (docs/)      5e7d15b9cf6ee7c3c3a51f008a483d75033332831fc0ca9726d9773b651c487a
> PACKAGE COPY           7a2bee57a8c3a6bf41f12f9fdf51a79cf201b44619fcf585e4ed5b2d220ff6ab
>   (Orientation/02_SUCCESSION/ in ORIENTATION.zip)
> ```
>
> The files are byte-identical except for **one load-bearing line** —
> item 1 of the six-item bootstrap:
>
> ```text
> THIS COPY     "read first, nothing else until the EPISTEMIC_PEER_CHECK
>                is complete"                                    ← WRONG
> PACKAGE COPY  "Read after baseline orientation when assuming a
>                predecessor's active role"                      ← repair
> ```
>
> `SEMANTIC DIVERGENCE != TEXTUAL DIVERGENCE` — a one-line collision is
> more dangerous than a large one, because it survives casual comparison.
>
> **Why this copy is wrong.** It instructs a receiving instance to read a
> succession artifact *before* baseline orientation. That inverts the
> entry path and contradicts the canonical orientation baseline
> (`Origin_Orientation_v0.1.9.md`), whose own BOOT INSTRUCTION directs an
> instance to read it first and treat `SUCCESSION/` as pull-only.
>
> **Scope boundary this collision violated:**
>
> ```text
> ORIENTATION       what project have I joined, and which rules do I accept?
>   != SUCCESSION   what state do I need to continue a predecessor's role?
>   != ROLE ELIGIBILITY   am I cleared to operate in that role?
> ```
>
> A lean handoff is **succession-scoped**. It is never the orientation
> entry point.
>
> **Current status of Lean Handoff v0.2 as a whole:**
>
> ```text
> THIS COPY (5e7d15b9)     RETIRED — preserved as failure evidence
> PACKAGE COPY (7a2bee57)  SUPERSEDE — carries a duplicated-phrase patch
>                          defect in item 1; not promoted here
> SAFE FOR SUCCESSION      NO — neither v0.2 copy is currently usable
> RECOMMENDED SOURCE       NEW SUCCESSOR (v0.3) REQUIRED — PENDING,
>                          deliberately not created by this cleanup
> ```
>
> **Authorship.** The defective read-first ordering in this copy
> originated with Claude and was repaired downstream without a version
> bump. Recording that here so the failure is inheritable rather than
> rediscovered.
>
> ---
>
> *Everything below this line is the retired v0.2 text, unchanged.*


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
