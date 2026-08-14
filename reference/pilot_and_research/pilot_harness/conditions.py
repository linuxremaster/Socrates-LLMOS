# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
§3 EXPERIMENTAL CONDITIONS + §14 RESOURCE NORMALIZATION.

Every condition shares one hard rule from §14: the token budget is a
SHARED TOTAL for the whole condition-trial, never per-agent. This module
enforces that mechanically via a Budget object that all agents draw from,
rather than trusting each agent call site to remember to divide correctly.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from llm_clients import LLMClient, CallResult
from substrate import SharedSubstrate
from verifier import verify_numeric_answer, extract_final_answer, VerificationResult
from tasks import Task

PROMPT_VERSION = "v0.2-frozen"

SYSTEM_PROMPT_SOLO = """You are solving a math word problem. Show your work \
briefly, then end your response with a line in exactly this format:
FINAL_ANSWER: <your answer as a number or simple expression>"""

SYSTEM_PROMPT_TEAM = """You are one of two agents collaborating on a math \
word problem via a shared workspace. You will see the current workspace \
contents below. Add your own hypotheses, calculations, or corrections. \
The workspace will NEVER contain the correct answer - only work-in-progress \
state and verification pass/fail events. Do not assume anything not shown \
in the workspace or the problem statement. When you believe the problem is \
solved, end your response with a line in exactly this format:
FINAL_ANSWER: <your answer as a number or simple expression>
If you are not ready to submit a final answer yet, omit that line."""


class BudgetExceededError(Exception):
    pass


@dataclass
class Budget:
    """Shared token budget for one condition-trial. §14: total, not
    per-agent. Every agent call must draw from the same Budget instance."""

    total_tokens: int
    used_tokens: int = 0
    model_calls: int = 0

    def remaining(self) -> int:
        return max(0, self.total_tokens - self.used_tokens)

    def charge(self, output_tokens: int | None) -> None:
        self.model_calls += 1
        if output_tokens is not None:
            self.used_tokens += output_tokens

    def request_allowance(self, requested: int) -> int:
        """Never let a single call request more than what's left."""
        return max(0, min(requested, self.remaining()))


@dataclass
class TrialOutcome:
    submitted_answer: str | None
    verification: VerificationResult
    model_calls: int
    verifier_calls: int
    input_tokens_total: int
    output_tokens_total: int
    wall_clock_seconds: float
    error_type: str | None
    substrate_log: list[dict] = field(default_factory=list)


def run_c1(
    task: Task, client: LLMClient, budget: Budget, max_rounds: int = 3
) -> TrialOutcome:
    """C1 — Single Agent + Verifier. No substrate, no second agent."""
    input_tok = output_tok = verifier_calls = 0
    submitted = None
    verification = VerificationResult(passed=False, reason="no_submission")
    error_type = None
    start_calls = budget.model_calls
    t0 = __import__("time").time()

    conversation = task.prompt
    for _round in range(max_rounds):
        if budget.remaining() <= 0:
            error_type = "budget_exhausted"
            break
        allowance = budget.request_allowance(min(1000, budget.remaining()))
        result = client.call(SYSTEM_PROMPT_SOLO, conversation, allowance)
        budget.charge(result.output_tokens)
        input_tok += result.input_tokens or 0
        output_tok += result.output_tokens or 0

        submitted = extract_final_answer(result.text)
        if submitted:
            verification = verify_numeric_answer(submitted, task.ground_truth)
            verifier_calls += 1
            break
        conversation = (
            task.prompt
            + "\n\nYour previous response did not include a FINAL_ANSWER "
            "line. Please provide one."
        )

    return TrialOutcome(
        submitted_answer=submitted,
        verification=verification,
        model_calls=budget.model_calls - start_calls,
        verifier_calls=verifier_calls,
        input_tokens_total=input_tok,
        output_tokens_total=output_tok,
        wall_clock_seconds=__import__("time").time() - t0,
        error_type=error_type,
    )


def run_team_condition(
    task: Task,
    client_a: LLMClient,
    client_b: LLMClient,
    budget: Budget,
    use_substrate: bool,
    max_rounds: int = 4,
) -> TrialOutcome:
    """
    Shared implementation for C2 (homogeneous+substrate), C3
    (heterogeneous, no substrate), and C4 (heterogeneous+substrate).
    Whether it's C2/C3/C4 is determined entirely by which clients are
    passed in and whether use_substrate is True - same code path, per
    §2.4 "evidence gates architecture," not three near-duplicate
    implementations that could silently drift apart.
    """
    substrate = SharedSubstrate(task.problem_id) if use_substrate else None
    input_tok = output_tok = verifier_calls = 0
    submitted = None
    verification = VerificationResult(passed=False, reason="no_submission")
    error_type = None
    start_calls = budget.model_calls
    t0 = __import__("time").time()

    transcript = ""  # used only when use_substrate=False (ordinary message passing)
    agents = [("agent_a", client_a), ("agent_b", client_b)]

    for round_num in range(max_rounds):
        for agent_name, client in agents:
            if budget.remaining() <= 0:
                error_type = "budget_exhausted"
                break

            if use_substrate:
                workspace = substrate.read_for_agent(agent_name)
                user_msg = f"PROBLEM:\n{task.prompt}\n\nWORKSPACE:\n{workspace}"
            else:
                user_msg = f"PROBLEM:\n{task.prompt}\n\nCONVERSATION SO FAR:\n{transcript}"

            allowance = budget.request_allowance(min(800, budget.remaining()))
            if allowance <= 0:
                error_type = "budget_exhausted"
                break
            result = client.call(SYSTEM_PROMPT_TEAM, user_msg, allowance)
            budget.charge(result.output_tokens)
            input_tok += result.input_tokens or 0
            output_tok += result.output_tokens or 0

            if use_substrate:
                substrate.write(agent_name, "note", result.text[:2000])
            else:
                transcript += f"\n[{agent_name}]: {result.text}"

            candidate = extract_final_answer(result.text)
            if candidate:
                verification = verify_numeric_answer(candidate, task.ground_truth)
                verifier_calls += 1
                submitted = candidate
                if use_substrate:
                    substrate.record_verification_event(
                        agent_name, verification.passed, verification.reason
                    )
                if verification.passed:
                    break
        if submitted and verification.passed:
            break
        if error_type == "budget_exhausted":
            break

    return TrialOutcome(
        submitted_answer=submitted,
        verification=verification,
        model_calls=budget.model_calls - start_calls,
        verifier_calls=verifier_calls,
        input_tokens_total=input_tok,
        output_tokens_total=output_tok,
        wall_clock_seconds=__import__("time").time() - t0,
        error_type=error_type,
        substrate_log=substrate.read_all() if substrate else [],
    )
