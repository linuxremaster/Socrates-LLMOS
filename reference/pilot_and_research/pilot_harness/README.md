<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Pilot Harness — v0.2 Frozen Spec

Automated implementation of the C1-C4 shared-substrate pilot, replacing
manual copy-paste relay. Implements the frozen spec's structural rules in
code rather than relying on prompt discipline alone:

- **§13 Substrate rule** (`substrate.py`) — ground truth is structurally
  kept outside the substrate object; writes that look like a final-answer
  assertion are rejected, not just discouraged.
- **§14 Resource normalization** (`conditions.py` `Budget` class) — one
  shared token budget per condition-trial, enforced mechanically so a
  two-agent condition can't silently draw double resources.
- **§13 Logging** (`logger.py`) — the exact field set from the spec,
  append-only, never overwritten.
- **§15 Stop conditions** — checked automatically after every trial where
  mechanically possible (error-rate spike, near-universal pass/fail).

## Setup

```bash
pip install sympy anthropic openai google-generativeai --break-system-packages
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
```

## Before running real trials

1. **Review and freeze `tasks.py`.** The 10 problems there are a
   starting placeholder I generated to meet §5's requirements
   (deterministic, auto-verifiable, no external knowledge, multi-step) —
   freezing the actual set is explicitly the human's authority per the
   spec, not something to inherit from me unreviewed.
2. **Confirm model names in `run_pilot.py` `build_clients()`** match
   what you actually intend to test — placeholders are marked.
3. **Dry-run first, zero cost:**
   ```bash
   python run_pilot.py --dry-run
   ```
   Prints the full randomized 120-trial plan without making any API calls.

## Running

```bash
python run_pilot.py --output-dir ./pilot_results --token-budget 4000
```

Interruptible — results.csv and state.jsonl are append-only, so a
Ctrl-C mid-run loses nothing already logged. Re-running does not
overwrite prior results (they'll accumulate; move or rename the output
dir between real runs if you want a clean file).

## What this does NOT automate (still needs you)

- **§7 Prompt Lock sign-off.** The prompts in `conditions.py` are written
  to match the spec's intent but are not the reviewed/frozen prompts from
  your actual relay discussion — check them against whatever you and
  ChatGPT/Gemini actually agreed to before running for real.
- **§12 Human Relay Protocol compliance** for anything outside this
  harness (e.g. if you manually intervene mid-run) — `logger.py` has a
  `log_human_intervention()` method; call it if you touch anything by
  hand.
- **The stop condition "the human relay materially changes model
  outputs"** — not applicable to this harness itself (it does not
  modify model outputs), but relevant if you fall back to manual relay
  for any trials.
- **§17-19 Method Ledger entries.** This harness produces evidence; it
  doesn't decide whether something becomes methodology. That's still a
  human/relay judgment call.

## Output files

- `pilot_results/results.csv` — one row per trial, matches §13 schema
- `pilot_results/state.jsonl` — raw event log: every substrate write,
  every human intervention, every auto-stop trigger
