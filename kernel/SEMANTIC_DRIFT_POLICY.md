<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Semantic Drift Policy v1.0

**Pairs with:** `growth_budget.py` (checks size drift). This checks
**meaning** drift — the gap that tool doesn't cover.

**Problem this closes:** a consolidation pass can be flat-or-shrinking on
line count (passes `growth_budget.py`) while still silently changing what
a rule means, or dropping a caveat that qualified it. The CORE vs.
1.3.6-C_clean audit found exactly this: `clean/HCF_LLMOS_Kernel_v1.3.6-C.md`
asserted "no new rules added" as fact; `core/KERNEL_STATUS.md` said the same
consolidation was "not yet verified" — and the clean package shipped
without that status file. Neither claim was wrong to *make*; the problem is
the claim outran the check behind it, and nothing flagged the mismatch.

**Design constraint:** this must stay cheap. A policy that requires full
formal proof of equivalence on every edit will slow development more than
the drift it prevents — that's the failure mode to avoid, not just an
aside.

---

## 1. Claim Tiers

Every consolidation, merge, or "cleanup" pass gets exactly one tier,
stated in the output file's header, next to the derivation note:

- **UNVERIFIED** — content was reorganized/compressed but not checked
  rule-by-rule against the source. Default tier. Nothing wrong with
  shipping at this tier — it just can't claim more than this.
- **SPOT-CHECKED** — a bounded sample of rules (see §2) was traced back to
  source and confirmed equivalent; the rest is inferred, not verified.
- **VERIFIED-EQUIVALENT** — every surviving rule was individually traced to
  its source provision and confirmed to carry the same operative meaning.
  Reserve this for cases where the cost is actually justified (e.g., before
  the file becomes the sole reference and the source is retired).

**Rule:** the header claim must not exceed the tier actually done. "No
rule content added" is a VERIFIED-EQUIVALENT-level claim; don't write it
at UNVERIFIED or SPOT-CHECKED tier — write what was actually established,
e.g. "Removal/merge only — not yet verified" (this is, notably, what
`KERNEL_STATUS.md` already said correctly; the fix here is making sure that
wording is what ships, not a stronger-sounding substitute).

## 2. Spot-Check Protocol (the cheap version — use this by default)

Full VERIFIED-EQUIVALENT is expensive; SPOT-CHECKED is the practical
default when a real check is warranted:

1. Pick every section that was **merged** (2+ source rules → 1) or
   **compressed** (elaboration cut, rule kept) — these are the two
   operations most likely to silently lose or shift meaning. Sections that
   were only **cut entirely** don't need this check; they're a scope
   decision, not an equivalence claim.
2. For each, read the surviving text and ask: *would someone who only has
   this version reach a different decision than someone with the
   original, in a case the original explicitly covered?* If yes, that's a
   drift event — fix the wording or flag it, don't ship it silently.
3. Log the sections checked and the result (pass / drift found and fixed /
   drift found and flagged) in one line each. This can go in the same
   ledger `growth_budget.py` already writes to — add a `"semantic_check"`
   field to that JSON line rather than starting a second log file.

This is bounded — a 20-section consolidation is a 20-item pass, not an
open-ended audit. That boundedness is what keeps it from becoming the next
slowdown.

## 3. Caveat-File Preservation

A status/caveat file (anything stating unresolved verification status,
open debt, or known limitations of the artifact it ships with) must not
be dropped when repackaging, unless the drop is logged with a reason.

- If the caveat has been resolved (e.g., SPOT-CHECKED was completed since
  the caveat was written), say so and drop it — that's legitimate.
- If it's dropped because the new package "is the clean version" and the
  caveat file wasn't part of that framing — that's not a resolution, it's
  a scope decision made silently. Don't do that. Either carry the caveat
  forward or state explicitly why it no longer applies.

## 4. Cross-Package Consistency Check

Before two packages describing the same artifact (e.g., a "full" and a
"clean" variant) ship together or in sequence, diff their status claims
specifically — derivation notes, change logs, any status file. A
disagreement between them about verification level is a finding to
surface, not something to resolve by picking whichever one reads better.
This is a specific case of the Kernel's existing Cross-Artifact
Consistency rule — this policy just makes it a required step at
consolidation time rather than something caught only if someone happens
to diff the packages later.

---

## Non-Goals

This policy does **not**:
- Require formal/automated semantic diffing — no tool currently does that
  reliably for prose rule sets, and building one would be a much larger
  and slower undertaking than the problem justifies.
- Apply to ordinary edits that aren't consolidation/merge/cleanup passes —
  routine additions or single-rule edits aren't in scope; this is
  specifically for the "reorganize N things into fewer things" operation
  where meaning-loss risk concentrates.
- Replace `growth_budget.py` or content-level human review — it's a third
  check alongside both, not a substitute for either.

## Compact Form (2026-08-14: symbol shorthand removed, see note)

A one-line-per-rule summary previously lived here using arrow/inequality
shorthand ("CLAIM ≤ VERIFICATION DONE", etc.). Removed during the
project's cross-model trust audit — that shape reads as command syntax
to at least one host model regardless of surrounding prose, and the
rules it restated already exist in full above (§1–§4). No content was
lost; only the symbol-only restatement was cut, same as the equivalent
change in `HCF_LLMOS_Kernel_v1.3.6-C.md`.

**End Semantic Drift Policy v1.0**
