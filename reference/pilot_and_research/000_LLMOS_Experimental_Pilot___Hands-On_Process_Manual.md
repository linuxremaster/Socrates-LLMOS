<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

LLMOS Experimental Pilot — Hands-On Process Manual

Status: Pilot execution manual
Purpose: Run the initial four-condition experiment consistently and produce an auditable result package.

---

1. What You Are Running

C1  Single LLM
    + Verifier

C2  Homogeneous Two-Agent Team
    + Shared Substrate
    + Verifier

C3  Heterogeneous Two-Agent Team
    + Chat
    + Verifier

C4  Heterogeneous Two-Agent Team
    + Shared Substrate
    + Verifier

The experiment tests whether heterogeneous models operating through a persistent external substrate provide measurable benefit over appropriate baselines.

---

2. Required Materials

- Two accessible, distinct LLMs.
- Python 3.
- SQLite.
- JSONL.
- SymPy.
- Frozen 30-problem pilot corpus.
- Frozen prompts and condition specifications.
- Machine-readable experiment ledger.
- Dedicated experiment directory.

---

3. Recommended Folder Structure

pilot/
├── spec/
│   ├── pilot_spec_v0.2.md
│   └── prompts/
│
├── problems/
│   └── problems.jsonl
│
├── runs/
│   ├── raw/
│   └── ledgers/
│
├── results/
│   ├── results.csv
│   └── analysis.md
│
└── method/
    └── method_ledger.md

---

4. Freeze Before Running

Before collecting experimental data, freeze:

- Problem corpus.
- Prompts.
- Agent roles.
- Four experimental conditions.
- Verifier behavior.
- 4,000-token shared total budget per condition-trial.
- Stopping rules.
- Interpretation rules.

Do not tune prompts against the evaluation problems.

---

5. Shared Substrate Rule

The substrate may contain:

- Work-in-progress state.
- Hypotheses.
- Calculations.
- Intermediate mathematical state.
- Provenance.
- Verification events.
- Verifier failures.

The substrate must not expose hidden ground truth.

ALLOWED

"Agent A proposed X."
"Expression failed verification."
"Current equation state is Y."


NOT ALLOWED

"Correct answer = Z."

The substrate is a shared computational state, not an answer oracle.

---

6. Run Each Problem

For every condition-trial:

1. Assign the randomized problem ID.
2. Initialize a clean condition state.
3. Start the global token counter.
4. Provide the identical problem to the appropriate condition.
5. Allow only that condition's defined communication and tools.
6. Record every model call.
7. Record input and output tokens.
8. Record substrate changes.
9. Record verifier events.
10. Terminate at the shared token limit.
11. Record the final answer.
12. Automatically verify the final answer.
13. Do not manually correct model reasoning.

---

7. Human Relay Rules

When the human acts as a relay:

- Copy/paste exactly.
- Do not summarize model output.
- Do not correct reasoning.
- Do not supply mathematical answers.
- Do not selectively omit inconvenient output.
- Log substantive human intervention.
- Remain blind to expected answers during execution where practical.

The human is currently a mechanical relay and experimental authority, not an additional reasoning agent.

---

8. Required Ledger Fields

Every trial should record:

run_id
problem_id
condition
agent_id
timestamp

input_tokens
output_tokens
total_tokens

substrate_state_before
action_taken
substrate_state_after

verifier_result
final_answer

human_intervention

---

9. Results File

Recommended minimum structure:

problem_id,condition,run,verified,total_tokens,final_answer,verifier_result

---

10. Primary Measurements

Measure:

Verified Accuracy

Percentage of trials producing a verifier-approved correct answer.

Token Consumption

Total model tokens consumed across the entire condition-trial.

Efficiency

Accuracy relative to token expenditure.

Secondary

Record verifier rejection and error-recovery events.

Defer elaborate semantic-distance or subjective collaboration metrics.

---

11. First Analysis

After execution:

1. Calculate verified accuracy by condition.
2. Calculate token expenditure by condition.
3. Calculate efficiency.
4. Compare C4 against appropriate baselines.
5. Examine verifier rejection events.
6. Examine obvious failure modes.
7. Record uncertainty and statistical limitations.

Do not convert a small pilot into a stronger conclusion than its sample supports.

---

12. Stop Rules

Do not expand the architecture merely because results are interesting.

Stop and reassess if:

- The full architecture produces no useful signal.
- Coordination costs substantially exceed benefits.
- The substrate introduces more problems than it solves.
- The pilot provides insufficient evidence to justify additional infrastructure.

A null result should not automatically be interpreted as proof that the underlying hypothesis is false.

---

13. End-of-Pilot Package

The completed experiment should produce:

pilot_spec_v0.2.md
problems.jsonl
raw_model_outputs/
run_ledgers/
results.csv
analysis.md
method_ledger.md

---

14. End-to-End Workflow

REQUIREMENTS
     │
     ▼
FROZEN SPECIFICATION
     │
     ▼
PROBLEM CORPUS
     │
     ├─────────┐
     ▼         ▼
    C1        C2
     │         │
     ├─────────┤
     ▼         ▼
    C3        C4
     │         │
     └────┬────┘
          ▼
        LEDGER
          │
          ▼
       RESULTS
          │
          ▼
       ANALYSIS
          │
          ▼
    METHOD LEDGER
          │
          ▼
    NEXT EXPERIMENT

Principle: Run the smallest experiment capable of answering the current question. Do not build the next layer until the evidence justifies it.