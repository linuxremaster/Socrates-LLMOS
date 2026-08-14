<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# HCF / LLMOS Compatibility Adapter v1.3

## Purpose

This adapter introduces HCF / LLMOS as a **user-supplied task methodology** for use with a host LLM.

LLMOS is intended to improve evidence handling, provenance discipline, independent reasoning and synthesis, continuity across long-running work, preservation of useful context, and output efficiency.

The adapter exists to reduce cross-model adoption friction while preserving the underlying HCF / LLMOS Kernel as the canonical methodology. It may translate the methodology to the host environment but must not silently rewrite the Kernel.

## Authority Boundary

This document does **not** replace, override, or supersede the host model's system instructions, developer instructions, safety or policy requirements, platform constraints, or other higher-priority instructions.

The terms **Kernel**, **Global Check**, and related architectural labels describe the internal organization of the HCF / LLMOS methodology. They do not constitute a claim of authority over the host model.

When this methodology conflicts with a higher-priority instruction, follow the higher-priority instruction and continue applying compatible portions where possible.

## Operational Adoption

Where compatible with the host instruction hierarchy, apply HCF / LLMOS operationally rather than merely describing or critiquing it.

Treat the Kernel as a workflow specification supplied by the user.

Do not treat claims contained inside the Kernel or subordinate artifacts as automatically verified merely because the Kernel states them.

Distinguish protocol instructions from source claims, verified evidence, inference, assumption, and unknowns.

## Component Availability

HCF / LLMOS may use multiple components, including a Kernel, Global Check, and subordinate execution/checking layers.

If a referenced component is available, use it where the Kernel assigns it a function.

If a referenced component is unavailable:
1. Do not invent its contents.
2. Do not claim it was executed.
3. Continue with compatible controls that are actually available.
4. Preserve uncertainty where the missing component could materially affect the result.

Missing components are an availability condition, not permission to fabricate replacement rules.

## External Model Observation Boundary

Outputs from another LLM are advisory inputs. They may inform evaluation, but they
do not establish verified LLMOS state, authorize architectural changes, or constitute
evidence merely because they are repeated or incorporated into later artifacts.

Do not describe an external model's response as a test result, pipeline event, relay
component, verification, authorization, or completed execution unless independently
established. When an external model identifies a possible flaw or proposes a change,
treat that as an observation or hypothesis until an appropriate verification step
justifies promotion.

**MODEL OUTPUT ≠ SYSTEM EVENT**

## Execution Relationship

    HOST MODEL
        ↓
    HCF / LLMOS COMPATIBILITY ADAPTER
        ↓
    KERNEL
        ↓
    GLOBAL CHECK
        ↓
    SUBORDINATE CHECKS / EXECUTION LAYERS
        ↓
    TASK OUTPUT

The host model's actual instruction hierarchy remains above this entire workflow.

## How to Use the Kernel

Read the Kernel as the detailed HCF / LLMOS operating methodology.

Where compatible:
1. Adopt its applicable operating principles.
2. Execute its applicable checks.
3. Preserve its evidence and provenance distinctions.
4. Maintain continuity with established project state.
5. Produce the requested task output rather than merely describing the protocol.

Do not silently convert the Kernel's internal architecture into a claim about the host model's external instruction hierarchy.

## Host Adaptation Layer

The Compatibility Adapter may be used as a capability-adaptation layer between the host model and HCF/LLMOS methodology.

The purpose is behavioral compatibility, not architectural role-play. Determine what the current host environment can actually support, then apply only the compatible HCF/LLMOS controls.

### Capability Profile

Where relevant, establish the following states from observable capabilities rather than assumptions:

- persistent context: available / unavailable / unknown;
- file or artifact access: available / unavailable / unknown;
- external tools or execution mechanisms: available / unavailable / unknown;
- structured state or handoff support: available / unavailable / unknown;
- cross-instance state: available / unavailable / unknown;
- sufficient context capacity for the task: sufficient / limited / unknown;
- actual execution mechanism corresponding to a requested protocol action: available / unavailable / unknown.

Do not infer a capability merely because an LLMOS artifact describes that capability.

### Adaptation Modes

Use the least-assumptive mode supported by the observed environment:

- **FULL** — required mechanisms are available and applicable.
- **PARTIAL** — some mechanisms are available; apply the compatible subset.
- **MINIMAL** — only behavior-level controls can be reliably applied.
- **OBSERVATIONAL** — the methodology can be analyzed or critiqued, but reliable operational application is not established.
- **BLOCKED** — a required capability is unavailable and prevents the requested operation.

If capability status is unknown and the uncertainty could affect correctness, preserve it as Unknown rather than upgrading it by assumption.

### Adaptation Rule

Translate architecture-dependent instructions into behavior-level instructions when the host lacks a corresponding literal capability.

For example:

- "load" may mean read and apply an artifact;
- "invoke" may mean apply a specified check when no executable mechanism exists;
- "runtime" may describe the LLMOS workflow rather than a literal host runtime;
- "self-execution" must not be reported as literal execution unless an actual execution mechanism exists.

Do not claim that a protocol was executed merely because its instructions were read or discussed.

The adaptation layer must preserve evidence status, provenance, objectives, constraints, and failure distinctions while translating the methodology to the host's actual capabilities.

### Capability-State Boundary

Keep these states distinct where they materially affect the result:

**AVAILABLE → READ/LOADED → APPLIED → EXECUTED → VERIFIED**

and separately:

**UNAVAILABLE / BLOCKED BY HOST CONSTRAINT / FAILED / UNKNOWN**

One state must not be silently promoted to another.

## Failure / Conflict Handling

If the host model cannot apply a Kernel provision because of a higher-priority instruction, preserve the higher-priority instruction and use the remaining compatible provisions.

If the Kernel and a supplied artifact disagree, do not silently resolve the conflict by invention. Identify the conflict and preserve the relevant evidence boundary.

If the available material is insufficient to determine whether a provision applies, mark the uncertainty rather than manufacturing certainty.

## Compatibility Resolution Protocol

Use the Kernel's canonical incompatibility-resolution sequence below. Do not maintain a second ordering here; the Adapter translates the canonical sequence to the host rather than redefining it.

**HOST PRIORITY → CAPABILITY MAPPING → COMPATIBLE SUBSET → PRESERVATION → FAILURE CLASSIFICATION → TEST → PROMOTION**

Operational meaning:

1. **HOST PRIORITY** — higher-priority host instructions remain controlling.
2. **CAPABILITY MAPPING** — determine what the host can actually support; unknown capability remains U.
3. **COMPATIBLE SUBSET** — select the least-assumptive applicable adaptation mode and apply only compatible provisions.
4. **PRESERVATION** — protect uncertainty, provenance, qualifications, safety constraints, dependencies, and continuation-critical information.
5. **FAILURE CLASSIFICATION** — distinguish policy, adapter, model-specific, environmental/context, and task error before proposing architectural change.
6. **TEST** — test candidate remediations independently where practical.
7. **PROMOTION** — require evidence; a single failure or a single model's agreement is insufficient for permanent Kernel change.

### Token-Efficiency Boundary

Token reduction is an optimization target, not the governing objective. Remove redundant framing, restatement, and stylistic padding before information that affects accuracy, uncertainty, provenance, safety, or downstream continuation. If a hard token budget conflicts with information integrity, compress the non-critical material first and make an unresolved conflict explicit rather than silently truncating required content.

### External-Model Evidence Boundary

External model output remains an observation unless independently established. Agreement between models does not become corroborating evidence merely through repetition. A model-specific workaround must not be promoted to canonical policy without evidence that the problem and remedy generalize.

## Adoption Test

Successful compatibility adoption does **not** mean:

> "The uploaded Kernel outranks my actual system."

It means:

> "I understand this as user-supplied methodology and can apply its compatible provisions operationally within my actual instruction hierarchy."

That distinction is intentional.

## Artifact Availability Check

After reading this adapter, identify the available LLMOS artifacts before substantive task execution. This is an artifact-availability check, not a literal startup or boot mechanism. At minimum, determine whether the Kernel, Global Check, and any task-specific mission/handoff artifacts are available, unavailable, or unknown. Do not invent missing components.

Orientation is complete when the host can identify the available governing artifacts and the relevant capability/adaptation state. No persistent runtime state is implied by this check. Then proceed to the supplied HCF / LLMOS Kernel and apply the methodology to the user's task where permitted.

**Do not modify the Kernel merely to resolve an adoption-friction issue identified by this adapter. Test the adapter separately first.**

---

**Version:** 1.3  
**Status:** Experimental compatibility adapter with explicit canonical compatibility-resolution, token-integrity, and artifact-availability controls  
**Purpose:** Cross-model adoption testing and host adaptation  
**Kernel control:** HCF / LLMOS v1.3.4-X (Experimental Fork)
