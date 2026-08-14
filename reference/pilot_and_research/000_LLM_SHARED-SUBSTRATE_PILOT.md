<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

LLM SHARED-SUBSTRATE PILOT

Human Operator Process Manual — v0.2

Purpose: Run the smallest trustworthy experiment, preserve everything needed to reconstruct it, and produce a clean result without methodological drift.

---

0. THE WHOLE EXPERIMENT AT A GLANCE

PREPARE
   │
   ▼
FREEZE EXPERIMENT
   │
   ▼
CREATE 10 PROBLEMS
   │
   ▼
RUN C1 ──┐
RUN C2 ──┤
RUN C3 ──┼──► COLLECT RAW DATA
RUN C4 ──┘
   │
   ▼
VERIFY / SCORE
   │
   ▼
LOCK RESULTS
   │
   ▼
ANALYZE
   │
   ▼
METHOD LEDGER
   │
   ▼
STOP / MODIFY / EXPAND

Do not redesign the experiment while running it.

---

1. CREATE THE EXPERIMENT DIRECTORY

Create one folder:

LLM_PILOT_V02/
│
├── 00_SPEC/
│   └── pilot_spec_v0.2.md
│
├── 01_TASKS/
│   ├── task_set.json
│   └── answers_private.json
│
├── 02_PROMPTS/
│   ├── C1.txt
│   ├── C2_A.txt
│   ├── C2_B.txt
│   ├── C3_A.txt
│   ├── C3_B.txt
│   ├── C4_A.txt
│   └── C4_B.txt
│
├── 03_RUNS/
│   ├── C1/
│   ├── C2/
│   ├── C3/
│   └── C4/
│
├── 04_LEDGER/
│   └── trials.jsonl
│
├── 05_RESULTS/
│   ├── scored_results.csv
│   └── pilot_analysis.md
│
└── 06_METHOD/
    └── method_ledger.md

Never overwrite raw runs.

---

2. FREEZE THE EXPERIMENT

Before running anything, save:

- Pilot specification v0.2
- Exact model identifiers
- Exact prompts
- Token-budget rule
- Task-generation procedure
- Verifier code
- Substrate schema
- Scoring procedure

Record:

experiment_version = v0.2
task_count = 10
runs_per_condition = 3
conditions = 4
token_budget = 4000 / complete condition-trial

After this point:

DISCOVERY ──X──► EXPERIMENT

No prompt optimization based on observed results.

---

3. GENERATE THE TASK SET

Create 10 algebraic/multi-step problems.

Each task receives:

problem_id
problem_text
ground_truth
verification_method

Example:

P001
P002
...
P010

Keep "answers_private.json" inaccessible to the models and human relay during execution.

Freeze the task set.

---

4. DEFINE THE FOUR CONDITIONS

                 VERIFIER
                    │
        ┌───────────┼───────────┐
        │           │           │
       C1          C2          C3/C4
        │           │           │
     ONE MODEL   SAME MODEL   TWO MODELS
                                │
                         ┌──────┴──────┐
                         │             │
                        C3            C4
                      CHAT        SUBSTRATE

C1 — Single Agent + Verifier

One model.

C2 — Homogeneous Team + Substrate

Two instances of the same model.

C3 — Heterogeneous Team + Chat

Two different models.

No persistent structured substrate.

C4 — Heterogeneous Team + Substrate

Two different models.

Persistent shared substrate.

All conditions receive equivalent verifier capability.

---

5. DEFINE THE SHARED SUBSTRATE

The substrate may contain:

✓ work-in-progress calculations
✓ hypotheses
✓ intermediate states
✓ task decomposition
✓ verification EVENTS
✓ verifier errors
✓ provenance

It must NOT contain:

✗ hidden ground truth
✗ private answer key
✗ externally supplied correct answer
✗ an oracle telling Agent B the final answer

A verification event may say:

Agent A submitted expression X
Verifier: FAIL
Error: inconsistent equation

It must not simply expose:

Correct answer = 47

The substrate is shared computational state, not an answer oracle.

---

6. TOKEN RULE

The 4,000-token limit applies to the entire condition-trial.

C1:
Model
└── maximum 4000

C2:
Agent A ─┐
         ├── TOTAL maximum 4000
Agent B ─┘

C3:
Agent A ─┐
         ├── TOTAL maximum 4000
Agent B ─┘

C4:
Agent A ─┐
         ├── TOTAL maximum 4000
Agent B ─┘

Do not give two-agent systems 4,000 tokens each.

Record actual usage when available.

---

7. RUN ONE TRIAL

For each:

problem × condition × repetition

create a unique:

run_id

Example:

P003_C4_R2

Then:

1. Load frozen problem.
2. Start clean condition state.
3. Initialize substrate if applicable.
4. Start token counter.
5. Send problem using frozen prompt.
6. Relay outputs mechanically.
7. Execute verifier when instructed/required.
8. Record state transitions.
9. Continue until:
   - verified solution,
   - failure,
   - or 4,000-token limit.
10. Save every raw output.
11. Save final result.
12. Do not modify the run afterward.

---

8. HUMAN RELAY RULE

If manual relay is necessary:

MODEL A
   │
   │ raw output
   ▼
HUMAN
   │
   │ exact copy
   ▼
MODEL B

The human may:

- copy;
- paste;
- execute the predefined verifier;
- record timestamps;
- record errors.

The human may NOT:

- solve;
- correct;
- paraphrase;
- select the better argument;
- reveal the expected answer;
- suggest a reasoning path.

If you intervene substantively:

HUMAN_INTERVENTION = TRUE

and record exactly what happened.

---

9. RAW DATA RECORD

Every trial produces one machine-readable record.

Minimum fields:

run_id
problem_id
condition
model_ids
prompt_version
timestamp
token_usage
model_calls
verifier_events
substrate_events
final_answer
pass_fail
human_intervention
failure_reason

Keep raw model outputs separately.

Raw data is immutable.

---

10. SCORING

After ALL trials are complete:

RAW RUNS
   │
   ▼
AUTOMATIC VERIFICATION
   │
   ▼
PASS / FAIL
   │
   ▼
scored_results.csv

Do not score while selectively looking for interesting outcomes.

Primary metric:

Verified Accuracy

Secondary:

- token consumption;
- efficiency;
- verifier rejection;
- correction events;
- substrate failures.

---

11. DO NOT INTERPRET RESULTS YET

First produce the complete dataset.

Then freeze it:

DATA COLLECTION COMPLETE
          │
          ▼
      DATA LOCK
          │
          ▼
      ANALYSIS

The 10-problem pilot is a signal-finding experiment.

A weak result does not automatically mean the hypothesis is false.

Classify:

SIGNAL
NO SIGNAL
NEGATIVE
INCONCLUSIVE

---

12. ANALYSIS QUESTIONS

Answer in this order:

Q1

Does C4 outperform C1?

Q2

Does C4 outperform C3?

If yes, the substrate may contribute something beyond heterogeneous chat.

Q3

Does C2 outperform C1?

If yes, multiple agents/shared state may contribute even without heterogeneity.

Q4

Does C4 outperform C2?

If yes, heterogeneity may contribute within the shared-substrate architecture.

Q5

What did the extra capability cost?

Compare:

accuracy
      ↕
tokens
      ↕
failures

---

13. INTERPRETATION GUARDRAIL

Never write:

«"The architecture works."»

Instead write:

«"Under this pilot configuration, C4 produced [observed result] relative to [baseline]."»

Then separate:

OBSERVED
   │
   ▼
INFERENCE
   │
   ▼
HYPOTHESIS

Do not collapse those categories.

---

14. METHOD LEDGER

After analysis, record only genuinely useful methodological discoveries.

For each:

METHOD:
What practice was discovered?

TRIGGER:
What problem caused it?

EVIDENCE:
What happened?

EFFECT:
What improved?

COST:
What complexity did it add?

STATUS:
Candidate / Tested / Supported / Rejected / Unresolved

The methodology evolves:

OBSERVE
   ↓
HYPOTHESIZE
   ↓
TEST
   ↓
RECORD
   ↓
COMPARE
   ↓
RETAIN / REJECT

Not:

Interesting idea
      ↓
Add another rule
      ↓
Add another rule
      ↓
Process creep

---

15. FINAL OUTPUT PACKAGE

The completed pilot should produce:

LLM_PILOT_V02/
│
├── SPEC
├── TASKS
├── PROMPTS
│
├── RAW RUNS
│     ├── C1
│     ├── C2
│     ├── C3
│     └── C4
│
├── trials.jsonl
│
├── scored_results.csv
│
├── pilot_analysis.md
│
└── method_ledger.md

The final analysis should contain:

1. What was tested
2. Exact conditions
3. Dataset
4. Resource usage
5. Results
6. C1–C4 comparisons
7. Unexpected observations
8. Experimental limitations
9. Methodological discoveries
10. STOP / MODIFY / EXPAND

---

16. THE MOST IMPORTANT RULE

When the pilot ends:

STOP.

Do not automatically build the next system.

Do not automatically increase the sample.

Do not automatically add another agent.

Do not automatically introduce Lean.

Do not automatically redesign the substrate.

The result becomes the evidence for deciding what happens next.

        PILOT
          │
          ▼
       EVIDENCE
          │
     ┌────┼────┐
     ▼    ▼    ▼
   STOP MODIFY EXPAND

The experiment is successful even if C4 fails.

A clean negative result can save substantially more time than an elaborate system built on an untested assumption.

The project's research loop is intentionally:

Question → Experiment → Evidence → Method → Next Decision

—not endless model-to-model discussion.