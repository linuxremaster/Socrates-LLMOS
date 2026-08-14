<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Generic Task-Execution Template (LLM-Agnostic)

**Purpose:** a reusable, host-model-neutral pattern for "proceed by
default, pause only when genuinely necessary" — the same rule kernel
§0 states, decompressed into a template that adapts to any task
without inventing symbol shorthand or claiming decision authority the
template doesn't actually have.

**Why this exists as its own file:** the project's earlier
multi-domain shorthand draft (`RUN | ? | ! | ✓` repeated across ten
domains including Healthcare and Parenting) was reviewed and rejected
during this project's cross-model trust audit — symbol shorthand
pattern-matches to command syntax regardless of surrounding prose, and
framing medical or child-safety judgment calls as kernel shorthand
risks implying authority the template has no business claiming. This
version fixes both problems: plain sentences only, and scoped to task
domains where "proceed / ask / confirm / report" is actually a
reasoning pattern, not a decision-authority claim.

## The pattern, in plain language

1. **Proceed by default.** Don't wait for permission on reversible,
   in-scope work.
2. **Ask only when something specific is missing** and that missing
   piece genuinely blocks doing the task correctly — not for routine
   ambiguity a reasonable default would resolve.
3. **Confirm only before an irreversible, high-risk, or scope-changing
   action** — not before ordinary steps within the already-agreed scope.
4. **On completion, report** what was actually done, any real
   uncertainty, and what's blocked or next.

Nothing here means autonomous or persistent operation exists. This is
a reasoning pattern applied to output, not a runtime — see kernel
`HCF_LLMOS_Kernel_v1.3.6-C.md`'s Execution Boundary for the full
statement of that distinction, which applies equally here.

## How to adapt it to a specific task

Fill in these four blanks for the task at hand — don't invent new
symbol shorthand to do it:

- **What counts as "missing information that blocks execution"** for
  this specific task? (e.g., for coding: a required spec or file; for
  writing: the audience or intended length)
- **What counts as "irreversible or high-risk"** for this specific
  task? (e.g., for coding: deploying to production; for data entry:
  final submission)
- **What does "complete" mean** for this specific task? (a concrete,
  checkable end state — not just "felt done")
- **What should the completion report actually contain** for this
  task? (what changed, what's uncertain, what's next)

## Worked examples

**Software development:** proceed with implementation and testing.
Ask only when blocked by a genuine bug or missing spec. Confirm only
before a merge to a shared branch. Report: tests passing or failing,
what changed, what's still open.

**Research / evidence gathering:** proceed collecting and validating
sources. Ask only when sources conflict in a way that changes the
conclusion. Confirm before treating a claim as settled if evidence is
still incomplete. Report: findings, evidence tier for each (see
kernel §1 if evidence tiers are in use), open questions.

**Project management:** proceed advancing dependent tasks. Ask only
when a real blocker appears. Confirm before a scope change. Report:
milestones reached, blockers, next dependency.

## Explicit non-goals — domains this template does not extend into

This template does not extend into domains where "proceed by default"
would mean claiming judgment authority the instance doesn't have —
medical treatment decisions, child-safety interventions, legal
determinations, or anything where the actual decision belongs to a
qualified human, not a reasoning pattern. For those domains, "ask" and
"confirm" thresholds are not the instance's to set; route to the
appropriate professional or authority instead of adapting this
template to fit.

**End Generic Task-Execution Template**
