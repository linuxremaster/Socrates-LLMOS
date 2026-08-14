<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Artifact-Delta Loop Detection Policy

**Scope:** detecting a stalled work loop — conversation continuing while
no real progress is being made. Kept separate from
`WELLBEING_FLAG_HANDLING_ADDENDUM.md` — a stalled loop and a wellbeing
flag are different failure modes and must not share a mechanism or a
lockout behavior.

**Origin:** developed across a five-pass review cycle between two
model instances (see `reference/` for the full revision history), then
adapted here with symbol shorthand removed per this project's
cross-model trust audit. Compares against an earlier "Socratic
Interruption Policy" proposal that detected loops from conversational
text variance alone — rejected because low text variance and a stalled
task are correlated but not the same signal, and the case where they
diverge (focused iterative work, e.g. a debugging cycle where prompts
look repetitive but the file keeps changing) is exactly where a
text-only signal produces a false positive.

## 1. Detection: artifact delta, not text variance

Don't measure how similar consecutive turns look. Measure whether a
checkable artifact actually changed between turns:

- **code:** diff of the actual file or function under discussion
- **claim:** evidence tier (Verified/Inferred/Assumed/Unknown) of the
  specific point in question
- **document:** whether a specific finding moved from open to resolved

**Loop state = several consecutive turns with zero artifact delta,**
regardless of how much text was produced. This is why a debugging
session with near-identical-looking prompts isn't flagged — the file
changes each turn — and why several turns of "you're right, nothing to
add" *should* be flagged even though each message differs slightly on
the surface: the underlying claim wasn't moving.

**Buildable now, no new infrastructure:** this needs a diff/hash check,
the same kind `pin-kernel` and `scan-secrets` already do — not
embeddings, and not a live multi-agent runtime.

## 2. Interrupt content: generated from the actual stalled item

When the gate fires, name the specific artifact that stopped moving —
not a generic clarifying question. For example: the last several turns
restate a claim without the underlying file or evidence tier changing;
what's the concrete next step that would move it, or is this actually
closed?

A scripted question that doesn't reference the real stalled state is
the same failure as a scripted agreement prompt, just pointed the other
direction — it must add something the conversation doesn't already
have, same test as kernel §5 Anti-Parroting.

## 3. No orchestration layer

There's no live multi-agent runtime to orchestrate here, only
sequential calls — a human relay or a coded pipeline. On gate-fire,
write a structured handoff record (same shape as `growth_ledger.jsonl`
— objective, evidence status, open items, blocker) and stop. The next
instance, or the next turn of this one, reads that record instead of
the raw stalled history. Convergence across instances means each one
independently checks the same artifact, not that they negotiate
agreement.

## 4. Unblocking

On resuming: load the existing handoff record, reset the loop counter,
and continue. No new protocol, no multi-step "resumption procedure" —
a later self-review pass in the original development cycle caught
exactly this kind of ceremony creeping back in after being ruled out,
and stripped it back out. Keep it stripped.

## 5. What this doesn't solve

- Doesn't catch a loop where the artifact *is* moving but pointlessly
  (churn without real progress) — that needs a task-specific "is this
  delta meaningful" check, which is domain-specific and not attempted
  here.
- Doesn't replace human judgment on when a genuinely open question is
  still open versus resolved — this gate flags *candidates* for
  interrupt, it doesn't auto-resolve them.

## Explicit anti-pattern this policy blocks

Continuing to produce text — reassurance, restated agreement, minor
rephrasing — while the actual work (the file, the claim, the open
item) stops moving, with nothing ever naming that it stopped moving.

**End Artifact-Delta Loop Detection Policy**
