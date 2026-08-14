# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Main entry point. Implements:
  §4  Pilot size (10 problems x 4 conditions x 3 runs = 120 trials)
  §8  Randomization of problem/run/condition order
  §14 Resource normalization (one Budget per condition-trial, shared)
  §15 Stop conditions (checked after every trial, not just at the end)
  §13 Logging (every trial written via PilotLogger)

Usage:
    python run_pilot.py --output-dir ./pilot_results --token-budget 4000

Requires API keys as environment variables (see llm_clients.py).
This makes real, billed API calls once you run it - nothing here calls
out on its own.
"""

from __future__ import annotations

import argparse
import random
import sys
import time
import uuid

from conditions import Budget, run_c1, run_team_condition, PROMPT_VERSION
from llm_clients import LLMClient
from logger import PilotLogger, TrialRecord
from tasks import TASKS

CONDITIONS = ["C1", "C2", "C3", "C4"]
RUNS_PER_CONDITION = 3  # §4


def check_stop_conditions(logger: PilotLogger, recent_outcomes: list) -> str | None:
    """
    §15 STOP CONDITIONS. Returns a reason string if the pilot should halt,
    else None. This is a best-effort automated check for the conditions
    that CAN be checked mechanically; some (e.g. "the human relay
    materially changes model outputs") still require human judgment and
    are not checked here - see README for what remains manual.
    """
    if len(recent_outcomes) < 5:
        return None

    recent = recent_outcomes[-10:]
    error_rate = sum(1 for o in recent if o.error_type is not None) / len(recent)
    if error_rate > 0.5:
        return (
            f"substrate/implementation instability: {error_rate:.0%} of last "
            f"{len(recent)} trials had an error_type set"
        )

    # near-universal success or failure across a meaningful sample
    if len(recent_outcomes) >= 20:
        pass_rate = sum(1 for o in recent_outcomes if o.verification.passed) / len(
            recent_outcomes
        )
        if pass_rate >= 0.98 or pass_rate <= 0.02:
            return (
                f"task difficulty produces near-universal "
                f"{'success' if pass_rate >= 0.98 else 'failure'} "
                f"({pass_rate:.0%} pass rate over {len(recent_outcomes)} trials) "
                f"- §15 requires stopping to redesign task difficulty"
            )

    return None


def build_clients() -> dict[str, LLMClient]:
    """Adjust model names here to match what you've actually validated
    against. These are placeholders - confirm before running real trials."""
    return {
        "claude": LLMClient("anthropic", "claude-sonnet-4-6"),
        "gpt": LLMClient("openai", "gpt-4o"),
        "gemini": LLMClient("google", "gemini-1.5-pro"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="./pilot_results")
    parser.add_argument("--token-budget", type=int, default=4000, help="§14 total per condition-trial")
    parser.add_argument("--seed", type=int, default=None, help="for reproducible randomization; omit for a real random run")
    parser.add_argument("--dry-run", action="store_true", help="build the trial plan and print it, make zero API calls")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    logger = PilotLogger(args.output_dir)

    # §8 randomize problem order, run order, condition order where practical
    trial_plan = [
        (task, condition, run_number)
        for task in TASKS
        for condition in CONDITIONS
        for run_number in range(1, RUNS_PER_CONDITION + 1)
    ]
    random.shuffle(trial_plan)

    print(f"Trial plan built: {len(trial_plan)} trials "
          f"({len(TASKS)} problems x {len(CONDITIONS)} conditions x "
          f"{RUNS_PER_CONDITION} runs)")

    if args.dry_run:
        for task, condition, run_number in trial_plan[:10]:
            print(f"  {task.problem_id} | {condition} | run {run_number}")
        print("  ... (dry run, no API calls made, no further trials shown)")
        return

    clients = build_clients()
    recent_outcomes = []

    for i, (task, condition, run_number) in enumerate(trial_plan):
        trial_id = str(uuid.uuid4())[:8]
        budget = Budget(total_tokens=args.token_budget)

        try:
            if condition == "C1":
                outcome = run_c1(task, clients["claude"], budget)
                model_desc = "claude-solo"
            elif condition == "C2":
                outcome = run_team_condition(
                    task, clients["claude"], clients["claude"], budget,
                    use_substrate=True,
                )
                model_desc = "claude+claude+substrate"
            elif condition == "C3":
                outcome = run_team_condition(
                    task, clients["claude"], clients["gpt"], budget,
                    use_substrate=False,
                )
                model_desc = "claude+gpt-no_substrate"
            elif condition == "C4":
                outcome = run_team_condition(
                    task, clients["claude"], clients["gpt"], budget,
                    use_substrate=True,
                )
                model_desc = "claude+gpt+substrate"
            else:
                raise ValueError(condition)
        except Exception as e:
            print(f"[{i+1}/{len(trial_plan)}] {trial_id} ERROR: {e}", file=sys.stderr)
            logger.log_state_event(
                {"type": "trial_exception", "trial_id": trial_id, "error": str(e)}
            )
            continue

        record = TrialRecord(
            trial_id=trial_id,
            condition=condition,
            problem_id=task.problem_id,
            run_number=run_number,
            model=model_desc,
            prompt_version=PROMPT_VERSION,
            timestamp=time.time(),
            input_tokens=outcome.input_tokens_total,
            output_tokens=outcome.output_tokens_total,
            model_calls=outcome.model_calls,
            verifier_calls=outcome.verifier_calls,
            submitted_answer=outcome.submitted_answer,
            pass_fail="PASS" if outcome.verification.passed else "FAIL",
            error_type=outcome.error_type,
            human_intervention=False,
            wall_clock_seconds=outcome.wall_clock_seconds,
        )
        logger.log_trial(record)
        for entry in outcome.substrate_log:
            logger.log_state_event({"type": "substrate_write", "trial_id": trial_id, **entry})

        recent_outcomes.append(outcome)
        print(
            f"[{i+1}/{len(trial_plan)}] {trial_id} {condition} {task.problem_id} "
            f"run{run_number} -> {record.pass_fail} "
            f"({outcome.output_tokens_total} out_tok, {outcome.model_calls} calls)"
        )

        stop_reason = check_stop_conditions(logger, recent_outcomes)
        if stop_reason:
            print(f"\nSTOP CONDITION TRIGGERED: {stop_reason}")
            logger.log_state_event({"type": "auto_stop", "reason": stop_reason})
            break

    print(f"\nDone. Results in {args.output_dir}/results.csv and state.jsonl")


if __name__ == "__main__":
    main()
