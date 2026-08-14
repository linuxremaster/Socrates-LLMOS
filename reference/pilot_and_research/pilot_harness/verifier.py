# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Deterministic verifier. This is the ONLY component in the whole harness
that ever sees ground truth. It reports PASS/FAIL to the caller and never
returns the ground-truth value itself, so there is no code path by which
an answer could leak into the substrate or into another agent's context.

Requires sympy. Install with: pip install sympy --break-system-packages
"""

from __future__ import annotations

from dataclasses import dataclass

try:
    import sympy
    from sympy.parsing.sympy_parser import parse_expr
except ImportError as e:  # pragma: no cover
    raise SystemExit(
        "sympy is required. Install with: pip install sympy --break-system-packages"
    ) from e


@dataclass
class VerificationResult:
    passed: bool
    reason: str  # short, safe to log/show — never includes ground truth


def verify_numeric_answer(
    submitted: str, ground_truth: str, tolerance: float = 1e-6
) -> VerificationResult:
    """
    Compare a submitted expression/value against ground truth using sympy,
    so "42", "42.0", and "84/2" are all treated as equivalent.

    submitted: the agent's final answer, as a string
    ground_truth: the frozen correct answer, as a string (caller-only —
        never pass this into substrate.write or any logging path that a
        model will see)
    """
    if submitted is None or submitted.strip() == "":
        return VerificationResult(passed=False, reason="empty_submission")

    try:
        submitted_expr = parse_expr(submitted, evaluate=True)
        truth_expr = parse_expr(ground_truth, evaluate=True)
    except Exception as e:
        return VerificationResult(passed=False, reason=f"parse_error:{type(e).__name__}")

    try:
        diff = sympy.simplify(submitted_expr - truth_expr)
        if diff == 0:
            return VerificationResult(passed=True, reason="exact_match")
        # fall back to numeric comparison for expressions that don't
        # simplify to exactly zero symbolically
        numeric_diff = abs(complex(diff.evalf()))
        if numeric_diff <= tolerance:
            return VerificationResult(passed=True, reason="numeric_match")
        return VerificationResult(passed=False, reason="mismatch")
    except Exception as e:
        return VerificationResult(passed=False, reason=f"eval_error:{type(e).__name__}")


def extract_final_answer(agent_output: str) -> str | None:
    """
    Convention: agents must emit their final answer on its own line as:
        FINAL_ANSWER: <expression>
    Returns None if no such line is found (counts as FAIL upstream —
    "no valid answer produced within the resource limit" per §9).
    """
    for line in agent_output.splitlines():
        line = line.strip()
        if line.upper().startswith("FINAL_ANSWER:"):
            return line.split(":", 1)[1].strip()
    return None
