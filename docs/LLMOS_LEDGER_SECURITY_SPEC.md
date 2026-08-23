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

Every event gets a real, permanent `event_id` (already true for
ledger entries via `observation_id`; needs to become universal, not
per-event-type) and a `content_hash` -- a hash of the event's own
content, computed once, unchanging. This is the foundation everything
else attaches to.

### 2. Append-chain / tamper evidence

```
event_hash = H(canonical_event_without_hash + previous_event_hash)
```

Not blockchain, not distributed consensus -- a simple hash chain,
periodically anchored somewhere independent of the ledger itself (git
history is the obvious candidate, already real and already used for
the kernel's own SHA-256 pinning). Makes silent retroactive edits or
deletions detectable, not impossible -- detectable is the actual goal.

**Real, existing tension to resolve, not new:** `ledger-compact`
already rewrites the ledger, replacing old raw entries with summaries.
That's genuinely useful for size management and was built deliberately
-- but a hash-chained ledger and a ledger that gets rewritten are in
real conflict. Whatever the chain design ends up being, it needs to
either exempt compaction explicitly (chain the summary events, not
pretend the originals are still individually verifiable) or redesign
compaction to preserve the chain. Not resolved here -- flagged as a
real, concrete design conflict for whoever implements this.

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

```
submission_id      unique forever, interface-generated (already in the
                    draft contract)
participant_id
participant_seq     monotonic per participant/session
received_at
content_hash
```

Canonical promotion rejects an already-consumed `submission_id`. This
is a general distributed-systems problem, not AI-specific -- the same
pattern any API with retries needs.

### 5. Revocation / supersession as new events, never destructive edits

```
event: ledger_status_change
target_id: <event_id>
old_status: ACCEPTED
new_status: REVOKED | SUPERSEDED | DISCONFIRMED
reason: ...
evidence: ...
```

The original event is never edited or deleted. Current effective
status is *computed* from the full history, not stored as a mutable
field. This is a direct generalization of something already real and
working: `record-outcome` already does exactly this for behavioral
observations (confirmed/disconfirmed, appended as a new fact, original
entry untouched -- used tonight, twice, on real findings). Same
pattern, applied to every event type, not just observations.

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

**Order, restated plainly:** identity + hash -> chain -> authenticated
participant identity -> replay semantics -> revocation as events ->
retrieval filtering -> capabilities -> only then, `/observations`.
