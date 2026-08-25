<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# LLMOS Ledger Security Specification — v0.1 (DRAFT, NOT IMPLEMENTED)

*Originally conceived as a conflict resolution management system; became this epistemic-discipline kernel and toolkit for LLM work through a real redirection -- see `docs/PROJECT_PRIORITIES.md`'s Origin and Scope Evolution section.*

**Status: design candidate. Nothing here is built.** Synthesizes a
two-round independent ChatGPT security audit of v0.10.0-alpha (both
rounds verified directly against primary sources before being treated
as reliable -- see `reference/external_ai_research_tracking.md`), plus
the architectural correction that came out of round two. This is the
spec `docs/LLMOS_SUBMISSION_CONTRACT_DRAFT.md` itself said to freeze
before any endpoint gets built -- this document is that freeze.

## The one architectural change this document makes to prior thinking

**`state/growth_ledger.jsonl` should not become the network-facing
global ledger.** It's a local append log designed for one human
operator, working well for that purpose all session. Bolting
authentication, replay protection, hash chaining, and revocation onto
that file format directly risks breaking what already works, and
conflates two different jobs: local operator convenience, and
adversarial-safe multi-participant persistence.

Instead: a security-aware event layer sits in front. `growth_ledger.jsonl`
becomes one *view* derived from that layer -- still real, still
readable the same way, still git-diffable -- not the thing directly
receiving untrusted submissions. What that layer's actual storage
looks like (still JSONL underneath, a real database, something else)
is an implementation choice for later; the point is it's no longer
assumed to be the same file the CLI already writes.

## The seven findings, as a build order

Not simultaneous -- each genuinely depends on the one before it.

### 1. Immutable event identity + content hash

**Corrected, 2026-08-22, after an external audit found a real
build-order gap:** the original wording here didn't specify *what* the
content hash actually covers, and the document's own final build order
implied identity+hash could precede authenticated participant binding
(point 3). If a hash is computed before authenticated origin metadata
is bound to the event, the hash doesn't protect that metadata --
identity could be swapped in afterward without invalidating the hash.
That's a real gap, not a hypothetical one, worth closing in the spec
even though nothing is implemented yet.

The correct pipeline order:

```
receive untrusted submission
        |
authenticate / bind origin           (point 3, moved earlier)
        |
assign immutable event_id
        |
canonicalize the COMPLETE event envelope
   (content + bound origin + timestamp, everything the hash must cover)
        |
content_hash = H(canonical envelope)
        |
replay / idempotency validation      (point 4)
        |
append / hash-chain                  (point 2)
```

`event_id` is permanent and real (already true for ledger entries via
`observation_id`; needs to become universal, not per-event-type).
`content_hash` is computed once, over the *complete* envelope
including bound origin -- not just the payload -- and is unchanging
from that point on. This doesn't require that authentication be
implemented before the local event store exists; it requires that
whenever authentication *is* added, the hash specification names
exactly which server-bound fields are inside the hashed envelope, so
the hash actually protects provenance rather than just payload text.

### 2. Append-chain / tamper evidence

```
event_hash = H(canonical_event_without_hash + previous_event_hash)
```

Not blockchain, not distributed consensus -- a simple hash chain,
periodically anchored somewhere independent of the ledger itself (git
history is the obvious candidate, already real and already used for
the kernel's own SHA-256 pinning). Makes silent retroactive edits or
deletions detectable, not impossible -- detectable is the actual goal.

**Resolved, 2026-08-22: the hash-chain vs. `ledger-compact` conflict
flagged in this document's first draft.** The fix isn't choosing one
feature over the other -- it's the standard event-sourcing separation:

```
CANONICAL EVENT LOG
  append-only, hash-chained, never rewritten
        |
        +--> CURRENT-STATE VIEW      (resolved/revoked/superseded state)
        +--> COMPACTED VIEW          (summaries, skeleton, working set)
        +--> RETRIEVAL INDEX         (searchable derived representation)
```

`ledger-compact` becomes a *projection* operation -- it produces a
disposable, rebuildable view for size/attention management -- not a
destructive rewrite of the canonical record. History stays immutable;
attention stays compressible. This is the same principle already
adopted for `docs/HOUSEKEEPING_AUDIT_CHECKLIST.md`-adjacent context
hygiene: compression manages what's actively attended to, not what's
epistemically true.

**Remaining, genuinely open decision, not yet made:** whether
`state/growth_ledger.jsonl` *is* the canonical event stream, or
becomes a derived compatibility view sitting on top of a separate
canonical store. It cannot be both a mutable working file and an
immutable security record at the same time -- that's the actual
choice this document defers, not the chain-vs-compaction conflict,
which is now resolved in principle above.

### 3. Authenticated participant identity, separate from payload

```
AUTHENTICATED CONNECTION
        |
server derives participant_id
        |
server binds identity to submission
```

Not:
```
payload says "I'm Claude"
        |
trust Claude
```

`propose-observation`'s current `instance` argument (self-asserted,
written directly as `proposed_by`) is fine for the existing
human-mediated local CLI workflow and should stay exactly as it is for
that use. It is explicitly not sufficient once a remote participant
can submit without a human directly invoking the command on their
behalf. The distinguishing question for any future transport: does
the *interface* assign identity, or does the *submission* claim it?
Only the former is acceptable for untrusted remote submission.

### 4. Replay / idempotency semantics

**Strengthened, 2026-08-22, after an external audit correctly found
"monotonic per participant/session" too loose for an adversarial
interface.** If sequences reset per session with no binding to *which*
session, an old message replayed into a new session could produce an
apparently-valid sequence number. `session_id` has to be part of the
identity, not an incidental field alongside it.

```
submission_id      unique forever, interface-generated (already in the
                    draft contract)
participant_id
session_id
participant_seq     monotonic within (participant_id, session_id)
received_at
content_hash
```

Explicit rule, not just structure:

- `(participant_id, session_id, participant_seq)` MUST be unique.
- `submission_id` MUST be globally unique.
- A retry with the same `submission_id` and identical `content_hash`
  is idempotent -- accepted silently, not treated as a new event.
- The same `submission_id` with a *different* `content_hash` is
  rejected as an integrity violation, not silently overwritten.

This gives deterministic behavior for both an ordinary network retry
(same ID, same content, safe to no-op) and a replay/tamper attempt
(same ID, different content, must be refused) -- the earlier looser
wording didn't distinguish these two cases explicitly.

### 5. Revocation / supersession as new events, never destructive edits

```
event A: ACCEPTED
event B: STATUS_CHANGE(target=A, REVOKED, reason, evidence)
event C: SUPERSEDES(target=A, replacement=D)
```

The original event is never edited or deleted. Current effective
status is *computed* from the full history, not stored as a mutable
field. This is a direct generalization of something already real and
working: `record-outcome` already does exactly this for behavioral
observations (confirmed/disconfirmed, appended as a new fact, original
entry untouched -- used tonight, twice, on real findings). Same
pattern, applied to every event type, not just observations -- widen
the existing, proven primitive rather than invent a parallel
revocation subsystem next to it.

### 6. Retrieval trust filtering and data-vs-instruction separation

Retrieved content carries its status, not just its text:

```
content
source
status
trust_level
created_at
revoked_at
instruction_authority = NONE   -- always, structurally, not by convention
```

Default retrieval excludes `PENDING`, `REJECTED`, `QUARANTINED`,
`REVOKED` unless explicitly requested. This directly extends the
submission contract's `CANONICAL DATA != EXECUTABLE INSTRUCTION`
principle to retrieval specifically: `handoff_rag` currently indexes
raw text with no trust-status filtering at all, and the relay
currently folds prior model outputs into ordinary conversational
history with no structural markup distinguishing data from instruction.
Both are real, current gaps this closes, not hypothetical future ones.

### 7. Participant capabilities, least privilege

```
Grantable:   READ_WORKING_SET, SUBMIT_OBSERVATION, SUBMIT_RESPONSE,
             PROPOSE_ACTION, REQUEST_RECALIBRATION

Never grantable to a remote participant:
             APPROVE, EXECUTE, CHANGE_POLICY, CHANGE_CAPABILITIES,
             DIRECT_LEDGER_WRITE
```

Identity and authority are different facts. Being authenticated as
"Claude-A" does not imply Claude-A may execute tools, propose code, or
read every ledger category -- each capability is granted separately,
narrowly, and explicitly.

**Real, first-party confirming evidence, 2026-08-25 (not hypothetical --
this actually happened during this project's own governance
discussion):** a ChatGPT instance reported having GitHub write
capability, reasoning from the fact that write *tools* were exposed by
its connector. Challenged rather than accepted, then tested live:
attempting to create a real GitHub issue returned `403 Resource not
accessible by integration`, reproduced on a second attempt. This
cleanly separates three facts that are easy to collapse into one:
**tool exposure** (the action appeared available) was true;
**authorization** (permission to actually use it) was false; the third
tier, **successful action**, was never reached. A capability model that
only checks whether an action is exposed, without separately verifying
authorization, would have accepted this participant as a write source
on the strength of a false positive. That's not a hypothetical risk
this section is designed to prevent -- it's a real one that occurred,
was caught by demanding a live test rather than accepting the report,
and resolved before any actual write was attempted on its strength.

**Scope of this finding, stated explicitly so it isn't over-generalized
later:** this confirms *this specific instance's connector, in this
specific integration state, on this date* was denied authorization
twice. It does not establish "ChatGPT cannot write to GitHub" as a
universal fact -- permissions can differ across accounts, connector
configurations, instances, and time. The reproduced, durable fact is
narrower and correspondingly stronger: *this handoff instance exposed
GitHub write actions but was denied authorization twice with HTTP
403.* Any future claim that a participant (ChatGPT, Gemini, a future
Claude session, anything) has write access needs its own live test at
the time it matters -- this entry is evidence the methodology works,
not a standing verdict on any participant's capability going forward.

### 7.5. Decision events -- human continuation/redirect authority,
distinct from capability facts

Added 2026-08-25, jointly designed with ChatGPT. Deliberately not
folded into section 7 above, even though it overlaps conceptually:
section 7 answers *what an actor is allowed or able to do* (a static
fact). This answers *when a human changed or extended the active
operating state* (a temporal transition). Different question, worth
its own category rather than stretching capability semantics to cover
it.

**Two decision types, and only these two:**

- **Continuation approval** -- explicit human authorization to let an
  AI continue operating past a natural checkpoint.
- **Directive change** -- explicit human redirection that changes the
  active task, objective, constraints, or route.

**Minimal schema:**

```
decision_event_id
timestamp
decision_type:      continuation_approval | directive_change
run/task/session_id
prior_state
new_state
stated_rationale
evidence/provenance_ref
outcome:             pending | completed | superseded | reversed
```

**Real, load-bearing restriction, not optional:** log only the
decision, its stated rationale, the affected task/run, and the
resulting state transition. Never infer or accumulate a profile of the
human from repeated decisions. Allowed: "continuation approved because
verification had passed and the next step was low-risk." Not allowed,
ever: "human tends to approve quickly," "human is risk-tolerant,"
"human usually redirects after disagreement," or any other
cross-event behavioral characterization of the person making the
decision. This isn't a stylistic preference -- it's the same boundary
this project's own memory-handling rules already draw around
psychological pattern-tracking of a real person, applied here
specifically because "decision telemetry" could otherwise drift into
exactly that without anyone deciding it should.

**Threshold for logging at all, to keep the category meaningful rather
than noise:** only log when the decision actually changes execution
state. An ordinary conversational "yes," "continue," or "sounds good"
does not automatically become a decision event unless it functions as
a real authorization or redirect. Uses `propose-observation`/
`log-observation` -- the existing tooling, not new infrastructure --
tagged with `decision_type`, cross-referenced to section 7's capability
facts when a decision event and an authorization question are actually
related, but tracked as its own event type.

## Byzantine participants -- what already helps, and the real remaining gap

Real, existing primitives that already partially address this, not
new: the human approval gate, provenance fields, evidence-tier
classification (A3), conflict preservation rather than forced
consensus (A7), and cross-model independent verification (used
repeatedly and successfully this session).

**The real, unaddressed gap:** multiple participants can produce
*apparent* independent agreement while actually sharing an unrecorded
common source, or influencing each other through the ledger itself.
Provenance-diversity checking only works if the shared source is
actually recorded -- nothing currently forces that, or detects when
it's missing. **Consensus is evidence about participant agreement, not
evidence about reality**, and no number of agreeing participants
should become sufficient for canonical truth on its own. This isn't
solved by anything in points 1-7 above; it needs its own future design
pass once real multi-participant submission actually exists to study.

**Review authority is kernel-defined, not identity-defined -- agreed
2026-08-25, committed here after being missed in the original
agreement.** No participant -- including whichever model is doing the
reviewing at a given moment -- becomes the privileged final check
merely by virtue of being "the one that's usually right" or the one
that happens to be coordinating a given exchange. What makes a review
valid is whether it points to the actual written criteria in this
document being satisfied, checkable by anyone regardless of which
model or instance performed it. This directly extends the same
Byzantine-robust-coordination principle above (real prior art:
arXiv:2507.14928, already logged in the research tracking file) from
"don't trust a coordinator's aggregation" to "don't trust a reviewer's
identity" -- same underlying failure mode, same fix.

## Plugin/execution boundary -- real, pre-existing, sharpened by this audit

Already true, already documented honestly in the code:
`require_trust = false` ships as the default, and imported plugins run
with full Python process privileges. Before any remote submission path
can reach anywhere near plugin discovery, one of these needs to become
true -- preferably both:

- Remote submissions can structurally never reach executable/plugin
  paths, regardless of what they contain.
- Production deployment requires `require_trust = true` with real
  pinned hashes, not the current development-friendly default.

## What this document does not resolve

Sequencing (build order above), not full designs, for most of these.
In particular: exact hash-chain anchoring mechanics, how capability
grants get issued and revoked in practice, and the Byzantine-collusion
detection gap are all real open problems, not just unwritten details.

**The one central, explicit open decision, narrowed by the
event-sourcing resolution above:** is `state/growth_ledger.jsonl` the
canonical append-only stream itself, or a derived view sitting on top
of a separate canonical store? Everything else in this document holds
either way -- this is the one choice that needs to be made, not just
sequenced, before implementation of points 1-2 can actually begin.

**Order, restated plainly, corrected 2026-08-22:** authenticate/bind
origin -> assign event identity -> canonicalize complete envelope ->
content hash -> chain (as canonical log + projections) -> replay
semantics -> revocation as events -> retrieval filtering ->
capabilities -> only then, `/observations`.
