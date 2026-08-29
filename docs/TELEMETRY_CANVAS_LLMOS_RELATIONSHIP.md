<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Socrates / Organic LLMOS — Telemetry Architecture Relationship and Current Operational Boundary

**Document type:** Project-level architecture clarification
**Status:** ADOPTED, 2026-08-29 (project experimental-boundary / architecture-clarification scope — not kernel policy)
**Canonical kernel status:** NON-CANONICAL
**Primary components discussed:** `Socrates_LLMOS` and `projects/telemetry_canvas/`
**Purpose:** Distinguish the integrated LLMOS telemetry architecture from the currently usable human-clocked web telemetry surface, and define their present relationship without implying capabilities that have not been implemented or verified.

---

## 1. Executive Summary

Socrates/Organic LLMOS and the Socrates Telemetry Canvas are related but distinct components.

The Socrates/Organic LLMOS package/runtime lineage is the broader project in which telemetry, persistence, governance, and related cognitive-state infrastructure are intended to operate as an integrated system.

`projects/telemetry_canvas/` is a separate, non-canonical, offline-first, human-clocked telemetry console designed for web-model workflows. It can capture manually relayed model responses, preserve literal text, generate structured telemetry events and surface detections, maintain a local hash-chained ledger, generate relay blocks, and export/import telemetry records.

At the present operational boundary, the Canvas is the available telemetry bridge for web instances. It is **not** equivalent to the integrated LLMOS runtime and does not establish that automated or asynchronous telemetry ingestion into LLMOS exists.

The current practical data path is therefore approximately:

```text
WEB MODEL INSTANCE
        |
        | human copies / relays prompts and responses
        v
HUMAN RELAY
        |
        v
TELEMETRY CANVAS
        |
        | structured capture / local ledger / export / relay
        v
EXPORTED TELEMETRY + PROJECT ARTIFACTS
        |
        | later review / ingestion / comparison
        v
SOCRATES PROJECT STATE
```

The intended future architecture may reduce or replace parts of this human relay with API, MCP, or another compliant asynchronous communication path, but that capability is **PENDING** unless separately implemented and verified.

---

## 2. Component A — Socrates/Organic LLMOS

### 2.1 Role

Socrates/Organic LLMOS is the broader project and architecture.

This document does **not** independently audit the full contents of that package on every revision and therefore does not claim that every intended telemetry capability is implemented, operational, or equivalent to the Canvas.

### 2.2 Intended Relationship to Telemetry

Within the broader architecture, telemetry is intended to support functions such as:

- preservation of observations and state transitions;
- provenance;
- epistemic classification;
- drift and anomaly tracking;
- handoff and continuity;
- longitudinal comparison;
- cross-instance and cross-model evaluation;
- recovery and audit.

The LLMOS side should be understood as the broader integration target rather than as a synonym for the current Canvas.

### 2.3 Current Limitation

Without a verified communication mechanism connecting web conversations to the LLMOS telemetry infrastructure, the existence of LLMOS telemetry code or schemas does not establish live telemetry capture from web instances.

The communication boundary matters.

A telemetry system that cannot receive the relevant event or response cannot independently log that event merely because the telemetry architecture exists.

---

## 3. Component B — Socrates Telemetry Canvas

### 3.1 Role

The Canvas identifies itself as:

- dynamic-prompt capable;
- kernel optional;
- offline-first;
- non-canonical.

Its embedded manual describes it as a **human-clocked external telemetry console for web LLM instances**.

This makes it an operational bridge for environments where direct automated access to the surrounding model conversation is unavailable.

### 3.2 Verified Functions in the Canvas

The Canvas source directly supports the following functions:

- external prompt-manifest loading;
- optional kernel loading;
- guided prompt queues;
- manual paste of complete model responses;
- preservation of literal response text;
- heuristic token estimation;
- deterministic lexical/surface detections;
- EPA-style evidence/provenance/authority fields;
- structured checkpoint validation;
- manual event entry;
- append-oriented local event recording;
- SHA-256 event hashing;
- hash-chain verification;
- local browser persistence where available;
- memory-only fallback when local persistence fails;
- compact relay generation;
- JSON and JSONL export;
- ledger import with chain verification;
- Markdown audit-report generation;
- evaluation JSON generation;
- deterministic self-tests.

### 3.3 Explicit Canvas Boundaries

The Canvas itself states important limits.

It does not automatically inspect provider-internal state.

It does not automatically read the surrounding web-model conversation.

It does not prove causal mechanisms.

It does not make model self-report independently true.

It does not convert lexical surface detections into findings.

It does not convert repeated agreement into verification.

A valid hash chain establishes sequence/content integrity under the implemented mechanism; it does not establish the truth or completeness of the observations contained in the chain.

These boundaries are central to the relationship between the Canvas and LLMOS.

---

## 4. The Current Operational Gap

The major current gap is **communication and ingestion**, not merely telemetry representation.

The web model, the Telemetry Canvas, and the broader LLMOS environment do not currently constitute one verified automated telemetry pipeline.

Human action presently connects them.

The human relay may:

1. issue or transfer a prompt;
2. receive the web model response;
3. paste the response into the Canvas;
4. initiate analysis/logging;
5. export or relay the resulting telemetry;
6. carry relevant state or artifacts into the broader Socrates workflow.

This is a **human-clocked telemetry pipeline**.

It should not be described as synchronous or asynchronous machine-to-machine telemetry unless such a path is separately established.

---

## 5. Why the Distinction Matters

Conflating the Canvas with LLMOS creates several risks.

### 5.1 Capability Overclaim

A future participant could incorrectly infer that web-instance telemetry is automatically entering LLMOS.

### 5.2 Provenance Loss

Manual relay is itself part of the evidence path. Hiding that step would make the provenance description inaccurate.

### 5.3 Automation Assumption

A telemetry schema or logger does not imply access to the source conversation.

### 5.4 False Persistence Claims

Local Canvas storage, exported telemetry, project files, conversational context, and LLMOS persistence are different storage/evidence surfaces.

They must not be treated as interchangeable.

### 5.5 Experimental Contamination

If manually transferred state is later interpreted as independently persistent model knowledge, continuity experiments can become circular.

The transfer mechanism must therefore remain visible.

**A specific, real instance of this risk, recorded 2026-08-29:** moving the Canvas from `reference/` (archived) into `projects/` (active project status) was, at the time of that move, explicitly confirmed to be an organizational status change only — not a claim that automated ingestion now exists. See `projects/telemetry_canvas/README.md` for the current statement of that boundary.

---

## 6. Current Architecture

The current operational relationship should be represented as:

```text
                    CURRENT WEB WORKFLOW

+-----------------------+
| Web model instance    |
| ChatGPT / Claude /    |
| Gemini / compatible   |
+-----------+-----------+
            |
            | manual interaction
            v
+-----------------------+
| Human relay           |
| observable transfer   |
| boundary               |
+-----------+-----------+
            |
            | paste / prompt / review
            v
+-----------------------+
| Telemetry Canvas      |
| non-canonical         |
+-----------+-----------+
            |
            | export / relay
            v
+-----------------------+
| Durable telemetry     |
| JSON / JSONL / MD /   |
| project artifacts     |
+-----------+-----------+
            |
            | bounded ingestion,
            | comparison or review
            v
+-----------------------+
| Socrates / Organic    |
| LLMOS project state   |
+-----------------------+
```

The human relay is currently a functional component of this path.

That fact should be recorded rather than abstracted away.

---

## 7. Intended Future Relationship

A future implementation may introduce a verified bridge such as:

```text
MODEL / PROVIDER
       |
       v
API / MCP / OTHER COMPLIANT RELAY
       |
       v
INGESTION + TELEMETRY ADAPTER
       |
       v
SOCRATES_LLMOS TELEMETRY
       |
       v
PERSISTENCE / ANALYSIS / RECOVERY
```

Such an architecture could potentially support asynchronous or lower-touch telemetry collection.

However, this diagram is a **design direction**, not a statement of current capability.

No future bridge should be considered operational until its transport, permissions, provenance, event semantics, failure behavior, and telemetry equivalence are tested.

---

## 8. Canvas as a Bridge, Not a Replacement

The Telemetry Canvas should not presently be framed as a replacement for LLMOS.

It is better understood as a **portable external telemetry surface and bridge**.

Its advantages include:

- browser-local operation;
- low infrastructure requirements;
- explicit human control;
- observable transfer boundaries;
- structured exports;
- deterministic validation;
- compatibility with manual web-model experimentation.

Its limitations include:

- human labor;
- manual transfer latency;
- possible copy/paste omission;
- inability to observe unrelayed conversation state;
- dependence on explicit export for durable external preservation;
- no direct evidence of provider-internal state;
- no automatic integration with the broader LLMOS runtime merely by existing, or by living in `projects/` rather than `reference/`.

The Canvas therefore provides useful telemetry under current constraints while leaving the integrated architecture as a separate engineering objective.

---

## 9. Human Relay as an Experimental Variable

Until a machine-mediated bridge exists, the human relay is not merely administrative overhead.

It is part of the experimental apparatus.

Possible human-relay effects include:

- selection of what is transferred;
- timing of transfer;
- accidental omission;
- formatting changes;
- choice of artifacts;
- interpretation during manual event creation;
- delayed propagation between participants.

Where these factors could affect an experiment, they should be recorded or controlled.

Human relay does not invalidate the experiment, but it changes what can legitimately be inferred from it.

---

## 10. Relationship to Cognitive Continuity

The distinction is particularly important for cognitive-continuity experiments (see `INSTANCE_LINEAGE_AND_SUCCESSION_SPEC.md` and its companion boundary document, where adopted).

If Instance B receives information because a human copied an artifact produced by Instance A, the observed continuity has an explicit transfer path.

The strongest immediate classification is therefore something such as:

**explicit information transfer** or **contextual inheritance**

rather than unexplained persistence.

Likewise:

```text
telemetry persistence ≠ model memory
context transfer ≠ identity continuity
shared artifact access ≠ shared hidden state
manual relay ≠ autonomous coordination
```

The telemetry architecture should make these distinctions easier to preserve.

---

## 11. Relationship to Instance Succession

The Canvas may also support the instance-lineage and succession process, where adopted.

For example, it may preserve:

- predecessor observations;
- handoff-related events;
- anomalies;
- corrections;
- lineage-relevant telemetry;
- exported evidence for successor review.

However, Canvas telemetry alone does not prove that a successor has inherited predecessor reasoning or behavior.

It records evidence that can later be evaluated.

---

## 12. Funding and Infrastructure Boundary

The current architecture is constrained by available access and infrastructure.

Potential future options may include paid API access, MCP-capable integrations, or other compliant communication mechanisms.

This document does not assume that any specific funding source, provider API, MCP implementation, or asynchronous relay will become available.

Until such a mechanism is implemented and verified, project documentation should describe the telemetry pipeline as **human-clocked**.

---

## 13. Epistemic Status

### VERIFIED

From the Canvas source, directly inspected:

- the Canvas is non-canonical, offline-first, and kernel optional;
- it supports manually pasted response capture;
- it records literal response text;
- it implements structured telemetry events;
- it implements SHA-256 event chaining and chain verification;
- it supports local persistence with a memory-only fallback;
- it supports JSON/JSONL export and verified-chain import;
- it generates compact relays and audit/evaluation reports;
- it explicitly limits its claims regarding internal state, causality, factual truth, and automatic chat access.

### INFERRED

Under the presently described project constraints, the Canvas functions as the practical telemetry bridge between manually operated web-model instances and durable Socrates telemetry/project artifacts.

### UNKNOWN

This document does not independently establish:

- the complete telemetry implementation inside the current LLMOS package;
- functional equivalence between Canvas telemetry and LLMOS telemetry;
- whether every Canvas event can be losslessly ingested into LLMOS;
- whether future API/MCP transport will preserve equivalent provenance;
- whether automated telemetry would alter participant behavior or experimental results.

### PENDING

- a verified automated or asynchronous ingestion path;
- telemetry equivalence testing between Canvas and LLMOS;
- formal mapping of Canvas event schemas into current LLMOS telemetry schemas;
- failure/recovery tests across the communication boundary;
- cost and access strategy for any future machine-mediated relay.

---

## 14. Governing Boundary

For current project work:

> **The Telemetry Canvas is the available human-clocked external telemetry surface. Socrates_LLMOS is the broader integration target. The existence of either component — including the Canvas's location in `projects/` rather than `reference/` — does not establish an automated connection between them.**

Any claim that telemetry moved from a web instance into LLMOS must identify the actual transfer mechanism.

If the transfer mechanism is manual, provenance should preserve that fact.

If the mechanism is unavailable or unclear, the transfer state is **UNKNOWN**.

---

## 15. Adoption Boundary

This document is a project-level architecture clarification, adopted at project experimental-boundary / architecture-clarification scope.

It does not modify the Canvas source or the LLMOS package itself.

It does not establish schema equivalence, runtime integration, or canonical kernel adoption.

Any future integration should be evaluated through the project's normal provenance, testing, review, and adoption procedures.
