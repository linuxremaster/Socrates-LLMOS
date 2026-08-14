<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

Organic LLMOS — Research, Relay & Experimental Development Manual

Status: Living process specification
Development model: Experimental, non-agentic, protocol-driven

---

1. Purpose

The LLMOS is not designed completely in advance.

It is developed experimentally.

The fundamental cycle is:

RESEARCH
   ↓
HYPOTHESIS
   ↓
EXPERIMENT
   ↓
EVIDENCE
   ↓
CRITIQUE
   ↓
METHOD
   ↓
NEW / IMPROVED COMPONENT
   ↓
NEXT CYCLE

A capability earns inclusion through evidence rather than conceptual appeal.

---

2. Core Principles

Build Bottom-Up

Start with the smallest useful process.

Do not prematurely construct:

- Full autonomous agent systems.
- Complex orchestration.
- Large infrastructure.
- Dynamic agent spawning.
- Unnecessary abstractions.

Think in LEGO Blocks

Each component should have an explicit interface:

INPUT
  ↓
OPERATION
  ↓
OUTPUT
  ↓
STATE CHANGE
  ↓
PROVENANCE
  ↓
STOP CONDITION

Components should be replaceable without redesigning the entire system.

Protocols Are Connectors

The interface between components should remain explicit even when implementations change.

COMPONENT A
     │
     ▼
 [PROTOCOL]
     │
     ▼
COMPONENT B

---

3. Current Relay Architecture

The current system uses four functional roles.

                         ┌──────────────┐
                         │    HUMAN     │
                         │ Experimental │
                         │   Authority  │
                         └───────┬──────┘
                                 │
             ┌───────────────────┼───────────────────┐
             │                   │                   │
             ▼                   ▼                   ▼
        ┌─────────┐         ┌─────────┐        ┌─────────┐
        │ GEMINI  │         │ CHATGPT │        │ CLAUDE  │
        │ Research│         │Integrate│        │Adversary│
        │  Scout  │         │ & Design│        │ Reviewer │
        └────┬────┘         └────┬────┘        └────┬────┘
             │                   │                   │
             ▼                   ▼                   ▼
          EVIDENCE            PROPOSAL            CRITIQUE
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 ▼
                           EXPERIMENT
                                 │
                                 ▼
                              RESULTS
                                 │
                                 ▼
                           METHOD LEDGER

These are functional roles, not permanent identities.

---

4. Role Definitions

Gemini — Research Scout

Primary question:

«What does existing evidence tell us?»

Responsibilities:

- Recent research.
- Peer-reviewed literature.
- Industry practice.
- Competing methodologies.
- Supporting evidence.
- Contradictory evidence.
- Evidence gaps.

Classify conclusions where appropriate:

ESTABLISHED
SUPPORTED
PARTIAL
UNCERTAIN
UNKNOWN

Research outputs are inputs to the process, not automatically facts.

---

ChatGPT — Integrator / Systems Designer

Primary question:

«Given the evidence, what is the smallest useful thing we should test?»

Responsibilities:

- Synthesize research.
- Identify the actual objective.
- Design experiments.
- Resolve material methodological problems.
- Simplify processes.
- Convert conclusions into executable protocols.
- Maintain architectural coherence.

---

Claude — Adversarial Reviewer

Primary question:

«Why might this proposed process be wrong?»

Responsibilities:

- Identify confounds.
- Challenge assumptions.
- Identify statistical weaknesses.
- Find alternative explanations.
- Find implementation ambiguities.
- Detect process creep.
- Identify missing controls.

The objective is not endless criticism.

The desired output is:

«What must be fixed before we run this?»

---

Human — Experimental Authority / Reference Implementation

The human currently performs functions that have not yet been safely formalized.

Responsibilities:

- Authorize experiments.
- Freeze specifications.
- Operate manual relay.
- Resolve genuine ambiguity.
- Observe process failures.
- Prevent unauthorized methodology drift.

The human should not silently solve the task for the system.

---

5. The Relay Process

The relay should increasingly move artifacts, not entire conversations.

GEMINI
  │
  │ Research
  ▼
RESEARCH ARTIFACT
  │
  ▼
CHATGPT
  │
  │ Synthesis / Design
  ▼
EXPERIMENT SPECIFICATION
  │
  ▼
CLAUDE
  │
  │ Adversarial Review
  ▼
CRITIQUE
  │
  ▼
CHATGPT
  │
  │ Resolve Material Flaws
  ▼
FROZEN SPECIFICATION
  │
  ▼
HUMAN
  │
  │ Authorize / Execute
  ▼
EXPERIMENT
  │
  ▼
RESULTS
  │
  ▼
METHOD LEDGER

---

6. Standard LLM Operation

A future LLM instance should receive an explicit operation.

RECEIVE
   ↓
ANALYZE
   ↓
CHALLENGE     ← when assigned
   ↓
RECORD
   ↓
HANDOFF

Receive

Establish:

- Objective.
- Current state.
- Evidence.
- Assigned role.
- Authority.
- Required output.

Analyze

Perform the requested operation.

Challenge

Attack assumptions when explicitly assigned.

Record

Convert useful conclusions into a durable artifact.

Handoff

Return only the information required by the next process component.

---

7. Evidence Model

Maintain explicit distinctions between:

Evidence

Observed or independently verifiable information.

Inference

A conclusion drawn from evidence.

Hypothesis

A proposition requiring testing.

Assumption

A temporary premise used to proceed.

Unknown

A proposition for which sufficient evidence is unavailable.

Avoid:

LLM assertion
      ↓
"fact"

without an evidentiary step.

---

8. Research Process

Research should answer a decision-relevant question.

Start with:

«What uncertainty could materially change what we do next?»

Then:

QUESTION
   ↓
SEARCH
   ↓
EVIDENCE MAP
   ↓
SUPPORTING / CONTRADICTORY EVIDENCE
   ↓
EVIDENCE GAPS
   ↓
CHEAPEST USEFUL TEST

Do not research indefinitely for theoretical completeness.

---

9. Anti-Rabbit-Hole Rule

Before investigating an issue:

«Will resolving this uncertainty materially change our next decision?»

YES → INVESTIGATE

NO  → DEFER

Interesting adjacent topics are not automatically relevant.

This protects against:

- Process creep.
- Premature abstraction.
- Metric inflation.
- Architecture inflation.
- Endless prompt optimization.

---

10. Experimental Discipline

Before an experiment:

1. Define the question.
2. Define the conditions.
3. Define measurements.
4. Define stopping rules.
5. Freeze the specification.

During the experiment:

- Do not optimize against emerging results.
- Do not add capabilities opportunistically.
- Do not alter controls.
- Do not tune prompts against evaluation data.

Afterward:

RESULT
   ↓
INTERPRETATION
   ↓
METHOD UPDATE

Execution errors and methodology changes should remain distinguishable.

---

11. Artifact-First Development

The system should progressively move:

CONVERSATION
     ↓
ARTIFACTS
     ↓
STRUCTURED STATE
     ↓
REUSABLE PROTOCOLS

Useful artifacts include:

research.md
evidence.json
critique.md
experiment_spec.md
prompts/
state.jsonl
results.csv
analysis.md
method_ledger.md

---

12. Methodology Ledger

The methodology itself is an experimental artifact.

For each proposed process change:

METHOD
What is proposed?

TRIGGER
What problem caused the proposal?

EVIDENCE
What demonstrated the problem?

CHANGE
What exactly changed?

RESULT
What happened?

COST
What complexity did it introduce?

STATUS
Candidate
Tested
Supported
Rejected
Unresolved

A suggestion does not automatically become methodology.

---

## 12A. Feedback Objective

Feedback is an optimization signal, not proof of correctness.

Prefer feedback that increases:

- Verified accuracy.
- Error detection and correction.
- Reproducibility.
- Evidence quality.
- Decision usefulness.
- Resource efficiency.

Do not treat the following as positive signals by themselves:

- Agreement.
- Confidence.
- Fluency.
- User satisfaction.
- Engagement.
- Output volume.
- Complexity.
- Novelty.
- Repetition.
- Apparent consensus.

When a process produces a positive result, ask:

1. What specifically improved?
2. What evidence demonstrates the improvement?
3. Could the result be caused by a confounding factor?
4. Is the improvement reproducible?
5. Should the underlying method or environment actually change?

Do not allow successful outcomes to automatically reinforce the process that produced them.

Use:

OBSERVE
  ↓
HYPOTHESIZE
  ↓
TEST
  ↓
VERIFY
  ↓
COMPARE
  ↓
RETAIN / REJECT

A useful feedback signal should improve the system's ability to distinguish what works from what merely appears successful.

### Feedback-Objective Principle

The system should preferentially amplify behaviors and methodologies that produce verified improvements, while resisting feedback loops that reward agreement, engagement, confidence, complexity, or other convenient proxies for success.

---

13. Process Self-Improvement

The relay generates methodological evidence.

INITIAL DESIGN
      ↓
REVIEW FINDS PROBLEM
      ↓
PROBLEM RESOLVED
      ↓
EXPERIMENT
      ↓
RESULT
      ↓
METHOD LEDGER
      ↓
FUTURE PROCESS

A process rule should enter the durable methodology only when sufficient evidence supports retaining it.

---

14. Human → LLM Substitution

The long-term objective is not simply to remove the human.

The objective is to determine which human functions can be reliably formalized.

HUMAN FUNCTION
      ↓
OBSERVE
      ↓
DESCRIBE
      ↓
FORMALIZE
      ↓
PROTOCOL
      ↓
LLM IMPLEMENTATION
      ↓
COMPARE
      ↓
VALIDATE
      ↓
AUTOMATE

The human initially acts as a reference implementation.

---

15. Non-Agentic First

Begin with explicit operations:

RECEIVE
   ↓
ANALYZE
   ↓
RECORD
   ↓
HANDOFF

Do not introduce autonomous planning merely because it is technically possible.

Agentic behavior should be introduced only when evidence demonstrates that its value justifies the additional complexity.

---

16. Architectural Emergence

The final LLMOS topology is not predetermined.

It may emerge as a network of validated components:

RESEARCH
    │
    ▼
SYNTHESIS
    │
    ▼
CRITIQUE
    │
    ▼
EXPERIMENT
    │
    ▼
VERIFICATION
    │
    ▼
PERSISTENT STATE
    │
    ├──────────────┐
    ▼              ▼
  HUMAN        LLM COMPONENT
    │              │
    └──────┬───────┘
           ▼
      NEXT PROCESS

Architecture grows by adding validated connections, not speculative machinery.

---

17. Decision States

Every significant proposal should reach one of four states:

RETAIN

Evidence supports continued use.

MODIFY

The concept appears useful but requires correction.

REJECT

Evidence argues against continuing.

DEFER

The question is interesting but not currently decision-relevant.

DEFER is a successful outcome when it prevents unnecessary work.

---

18. Review Protocol for Other LLMs

When another LLM reviews this document, it should first evaluate:

DRIFT

Has the document claimed more than the evidence supports?

CONFOUNDS

Does a process test multiple variables without isolating them?

PROCESS CREEP

Has unnecessary complexity entered the system?

AMBIGUITY

Could two operators interpret the same rule differently?

AUTOMATION READINESS

Is a human function sufficiently understood to formalize?

EVIDENCE GAP

Is an architectural claim unsupported?

STOPPING

Is there a clear point at which additional work should stop?

Return:

CRITICAL ISSUES
What must change?

OPTIONAL IMPROVEMENTS
What could change but does not need to?

DRIFT DETECTED
Where has the document exceeded its evidence?

UNCHANGED ELEMENTS
What should remain frozen?

RECOMMENDATION
RETAIN / MODIFY / DEFER / REJECT

Do not rewrite the document merely because improvements are imaginable.

---

19. Current North Star

The working hypothesis is:

«A useful computational system may emerge from heterogeneous LLMs, humans, deterministic substrates, persistent state, protocols, and verification mechanisms connected through experimentally validated interfaces.»

This remains a hypothesis.

The architecture must remain evidence-gated.

---

20. Development Rule

KEEP COMPONENTS SIMPLE.
KEEP INTERFACES EXPLICIT.
KEEP STATE PERSISTENT.
KEEP AUTHORITY BOUNDED.
KEEP EXPERIMENTS SMALL.
KEEP ARTIFACTS.
KEEP THE HUMAN WHERE NECESSARY.
AUTOMATE DEMONSTRATED BEHAVIOR.
DEFER UNNECESSARY COMPLEXITY.

Most importantly:

«Let the architecture emerge from what survives experimentation.»

---

21. Overall Direction

The project should continuously move toward:

CONVERSATION
     ↓
RELAY
     ↓
PROTOCOL
     ↓
ARTIFACT
     ↓
STATE
     ↓
EXPERIMENT
     ↓
EVIDENCE
     ↓
VALIDATED COMPONENT
     ↓
AUTOMATION
     ↓
LLMOS

Not:

CONVERSATION
     ↓
MORE CONVERSATION
     ↓
MORE PROMPTS
     ↓
MORE COMPLEXITY
     ↓
PROCESS CREEP

The objective is not to make the relay increasingly elaborate.

The objective is to make the relay progressively less necessary as reliable protocols and components emerge.