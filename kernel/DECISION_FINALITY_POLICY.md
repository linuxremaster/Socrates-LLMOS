<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Decision Finality Policy

**Type:** process/policy, not new software architecture. Net effect:
subtraction — removes a requirement, adds nothing structural.

**Origin:** re-confirming settled decisions across multiple model
instances or providers was adding latency without adding correctness —
a conclusion reasoned through completely doesn't become more correct by
being repeated to a second instance. The Rule 6 amendment is the
counter-example this generalizes: reasoned through completely,
corrected once mid-discussion, converged, in one conversation, no
arbitration architecture involved.

**What this is not:** a gateway, arbitration layer, voting mechanism,
or consensus threshold. No new software component. Nothing here routes
a decision through multiple models automatically or requires their
agreement before it takes effect — that kind of system was considered
and rejected earlier in this project's review; it doesn't reduce
disagreement, it adds a stage before disagreement gets resolved.

## 1. Decisions are final where they're reasoned through — a concrete test, not a feeling

A decision counts as settled once it passes this test, not merely once
it *feels* resolved:

**Can you state what would have changed the conclusion?** If the
answer is a real alternative that was actually considered and ruled
out on its merits, the decision is settled. If the honest answer is
"nothing, it just felt done" or "no one raised anything," treat it as
provisional, not settled — that's the same fresh-pass test the kernel
already applies to cross-model provenance (§9), applied here to
single-conversation decisions.

**A decision that included real friction — a correction, a changed
mind, an objection actually worked through — is stronger evidence of
genuine reasoning than one that converged instantly with no pushback.**
Instant convergence isn't automatically wrong, but it's weaker
evidence, and shouldn't be treated as equally settled without at least
noting that no alternative was seriously tested.

This test exists specifically because the pressure that motivates this
whole policy — friction, fatigue, wanting to be done — is the same
pressure that could make "reasoned through completely" a rubber stamp
if left as a feeling rather than a check.

## 2. Named high-stakes categories that stay on slow, deliberate review — not a vibe-based carve-out

These stay outside this policy's speed-up, explicitly, regardless of
how settled a single conversation feels:

- Any change to `WELLBEING_FLAG_HANDLING_ADDENDUM.md`'s actual
  triggers or thresholds — what counts as a flag, when to name it, when
  to stop.
- Any change to kernel §20 Priority order, or to what counts as
  system/safety authority above the kernel.
- Any change that **loosens** a safety-relevant rule rather than
  tightening or clarifying it — a stricter version of an existing rule
  can move fast; a looser one cannot.
- Any change to this policy itself, or to
  `ARTIFACT_DELTA_LOOP_DETECTION_POLICY.md`'s loop-detection mechanism —
  policies that govern how decisions get made shouldn't be amended
  under their own sped-up process.

A change outside these categories, that passes the test in §1, is
settled without further re-confirmation. A change inside these
categories gets the slower, more deliberate review this policy doesn't
try to speed up — full stop, not a judgment call made mid-conversation
by whichever instance happens to be reasoning at the time.

## 3. Decision-making threads vs. testing/audit threads — different purposes, not the same "parallel threads" problem

Point 4 below discourages opening the *same undecided question* in
parallel across conversations. It does not discourage, and should
never be read as discouraging, deliberate cross-model testing or
auditing — like the ChatGPT relay testing this project's own
cross-model trust boundaries. That's adversarial probing for blind
spots, a different purpose from resolving an open decision, and this
policy doesn't apply to it. Running the same audit through multiple
models on purpose is not "asking the same question in more places than
it needs to be" — it's the thing the question is trying to test.

## 4. Fewer parallel threads per decision

Where possible, a given decision (a specific rule, a specific file) is
worked through in one continuous line of reasoning from open question
to resolution, rather than opened in parallel across several
conversations simultaneously. Parallel threads on the *same undecided
question* are the main source of the "competing right answers"
problem — not a sign arbitration infrastructure is needed, but a sign
the same question is being asked in more places than it needs to be.

**A resumed session counts as one continuous line of reasoning, not a
new instance re-litigating from scratch**, provided it picks up from
the prior session's actual handoff artifact (`rag/SESSION_HANDOFF.md`,
`state/growth_ledger.jsonl`) rather than starting cold. The distinction
that matters is whether context carried forward, not whether it
happened in a single sitting.

## 5. Human synthesis remains available, and is not automated

The person running this project may still consult multiple models and
compare their answers manually — that's synthesis work only a human
can meaningfully do, since it requires judgment about which points
actually matter, not just aggregation. This doesn't restrict that. It
restricts building a mechanism that performs this comparison
automatically and gates implementation on its output.

## 6. Disagreement, when it happens, is resolved by direct comparison

If two conclusions from separate conversations genuinely conflict on
substance (not just phrasing), the resolution path is: bring both into
one conversation, state the conflict plainly, and reason it through
there — the same method that resolved Rule 6. Not a new component; an
existing capability, applied deliberately instead of building around
it. **Reopening a settled decision uses this same path, not a return
to multi-instance re-confirmation** — if new evidence or a real
objection surfaces later, it gets reasoned through directly, the same
way the original decision was.

## What this changes operationally

- Removes any requirement, explicit or de facto, that a kernel or
  document change needs sign-off from more than one model instance
  before it's considered real — except the named categories in §2.
- Stops treating "instance B hasn't reviewed this yet" as a blocking
  condition for something already reasoned through and passing the §1
  test.
- If multiple audits already exist for something, the person may still
  read them for input, but implementation doesn't wait on them
  converging first.

## Non-goals

- Does not remove human review — the person remains the actual
  authority on what ships.
- Does not claim any past disagreement between instances was wrong to
  have — disagreement is fine; this targets the process of resolving
  it, not its existence.
- Does not apply to the categories named in §2, where slower deliberate
  review is warranted on the merits regardless of how settled a single
  conversation feels.
- Does not discourage deliberate cross-model testing or auditing (§3)
  — only same-question parallel re-litigation.

**End Decision Finality Policy**
