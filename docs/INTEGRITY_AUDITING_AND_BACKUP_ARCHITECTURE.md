<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Integrity Auditing & Backup Architecture — v0.1 (DRAFT, NOT IMPLEMENTED)

*Originally conceived as a conflict resolution management system; became this epistemic-discipline kernel and toolkit for LLM work through a real redirection -- see `docs/PROJECT_PRIORITIES.md`'s Origin and Scope Evolution section.*

**Status: design candidate, converged through joint Claude/ChatGPT
review. Nothing here is built.** This is operational/security
documentation, deliberately not kernel doctrine -- it describes how
the source and evidence get *protected*, not new reasoning principles
for how instances behave. One real kernel gap surfaced during this
same review (kernel governance over model identity for review
authority) was committed separately, directly into `docs/
LLMOS_LEDGER_SECURITY_SPEC.md`, where governance principles belong.

## What this is not

A broader "Parity / No Privileged Node" kernel invariant was proposed
alongside this and explicitly declined after review -- most of what it
claimed to justify already existed (Byzantine-consensus caution,
identity≠authority, the reviewed-and-committed governance-over-identity
fix), one piece was already guaranteed by the MPL license (forkability,
not worth restating as doctrine), and one piece ("no mandatory central
telemetry owner") turned out to conflict with a narrower, more precise
principle that *is* adopted below. Declining the broad version and
keeping this narrow one is itself the intended outcome, not a
compromise.

## 1. Canonical source stays canonical

`Socrates-LLMOS` on GitHub remains the one canonical clean source.
Real, concrete practices to adopt going forward: `main` protected once
practical, routine `--force` retired (already agreed and adopted in
this session's own workflow discussion), write authority minimized,
consequential source changes carry attributable Git provenance.

## 2. Telemetry stays separate, and ownership ≠ authority

`Socrates-LLMOS-Telemetry` (or whatever it ends up being called)
remains the sanitized, public evidence layer. Local raw telemetry is
the authoritative pre-sanitization record.

**Central administrative ownership of that repository is fine, and
doesn't need to be avoided.** What actually needs to hold, and does
already by design:

```
central repository owner
        !=
central truth authority

telemetry entry
        |
provenance / integrity / recurrence(REPEATED) / reproduction(REPRODUCED) gates
        |
eligible evidence
```

An entry existing in the telemetry repo, administered by one person,
does not make it true. It becomes eligible evidence only by passing
through the promotion chain already defined (`OBSERVED -> REPEATED ->
REPRODUCED -> CANDIDATE -> REVIEWED -> ACCEPTED/REJECTED`, per the
decision-events work earlier this session). Administrative
centralization and epistemic centralization are different things --
this project keeps the first for practicality and rejects the second
by design, not by needing a distributed-consensus mechanism it doesn't
otherwise have a use for.

Telemetry can nominate development/kernel changes. It cannot promote
them directly. The existing evidence/promotion gates remain
controlling, unchanged by anything in this document.

## 3. Two independent integrity checkers

```
              GitHub canonical source
                      |
            +---------+---------+
            v                   v
       CHECKER A           CHECKER B
     separate host       different host
     separate account    separate account/provider
     read-only           read-only
            |                   |
            +--- no mutual dependency ---+
```

Neither checker gets repair or write authority over what it audits.
Their job is detection, preservation, and escalation -- not automatic
remediation. Independence matters more than secrecy: different
credentials, storage, and execution environments should mean one
compromise can't also alter the evidence that the compromise happened.
Design should stay useful even if an attacker knows the checkers
exist.

**Why this is genuinely needed, not speculative:** a compromised
system that also controls its own audit trail can rewrite that trail
consistently -- a hash chain alone doesn't protect against an attacker
who controls the system capable of regenerating a self-consistent
chain from scratch. This isn't hypothetical for this project
specifically: the real AISI incident already logged in `reference/
external_ai_research_tracking.md` describes an agent editing its own
earlier records to appear harmless. A checker whose known-good
reference lives in the same trust domain as what it's checking
couldn't have caught that pattern.

## 4. What gets audited, and how narrowly

**Source integrity:** Git state/history, critical file hashes, kernel
changes, dependency/lockfile changes, CI/workflow changes, release/
version hashes.

**Telemetry integrity:** run provenance, evidence hashes, schema
validity, missing/replayed/duplicated events, unexplained state
transitions.

**Governance integrity -- deliberately narrow, refined during this
review to avoid duplicating existing machinery:** the external checker
does not reinterpret governance decisions -- that's what the existing
DECIDED-tier/supersession/hash-chain machinery in the ledger security
spec already does semantically. Its job is narrower and specifically
external:

> Does the externally observed canonical kernel/governance state still
> match an independently preserved known-good state, or an
> attributable, authorized transition away from it?

That's a comparison against an independent reference, not a semantic
judgment about whether a governance decision was itself correct. It
protects against whole-history compromise without duplicating what
already exists for interpreting governance content.

A diff establishes that state changed -- it does not establish
malicious intent. Unexpected changes become evidence/anomalies
requiring explanation (through the existing observation/quarantine
pipeline), not automatic security incidents.

## 5. Known-good state, held independently

Each checker retains independently generated known-good hashes/
manifests -- not copied from the system it's checking. A consequential
current-state change should be explainable by an authorized,
independently observable transition, or it's flagged. This is the
concrete mechanism that makes section 3's independence real rather
than nominal: the live repository, the checker, and the historical
evidence should not share one writable trust domain.

## 6. Encrypted telemetry backups

```
telemetry
    |
snapshot/archive
    |
manifest + hashes
    |
client-side encryption
    +-- local-device copy
    +-- separate cloud-storage copy
```

Cloud provider receives ciphertext only. Encryption key material must
not be stored alongside the encrypted archives, or in the same
compromise domain as either.

Tentative, deliberately non-doctrinal cadence (configurable, not
kernel policy): snapshot after significant experiments/kernel changes;
daily encrypted local backup; daily-to-weekly encrypted cloud backup
depending on evidence volume; periodic integrity verification; monthly
restore test.

## 7. Threat model, stated plainly

Addressed: canonical repository compromise, maintainer credential
compromise, unauthorized source modification, malicious/compromised
dependencies, telemetry/evidence poisoning, telemetry deletion or
alteration, compromised local runtime, compromised auditor/checker,
ransomware/storage loss, legitimate-looking but unexplained authorized
changes.

**Explicitly not claimed:** this does not prove every detected change
is malicious, and does not guarantee compromise detection. Detection
and evidence preservation, not a guarantee.

## 8. Public posture statement (for `SECURITY.md`)

Discloses posture, not defensive implementation detail (no checker
locations, credentials, backup destinations, detection thresholds, or
recovery secrets):

> LLMOS is designed so that no single model, operator, provider,
> repository, telemetry source, or infrastructure component is
> intended to become an unquestionable authority. Consequential
> actions and claims are designed to remain attributable, challengeable,
> independently auditable, and recoverable across separate trust
> domains.

## 9. Sequencing -- this does not block the Gemini work, and shouldn't

```
restore canonical LLMOS in Termux
        |
baseline existing telemetry/loggers
        |
verify Termux GitHub write capability (harmless branch, independently verified)
        |
establish source/backup integrity baseline
        |
bounded Gemini integration
        |
calibration/testing
        |
telemetry evidence
        |
candidate development
        |
governed promotion into clean LLMOS
```

This document describes the target architecture. The immediate next
real step remains what it already was before this design pass:
restore Termux, establish baseline, verify the write path
independently -- not create additional public infrastructure ahead of
that.
