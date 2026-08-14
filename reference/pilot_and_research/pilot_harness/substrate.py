# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Shared computational substrate for the C2/C3/C4 conditions.

Enforces §13 SHARED SUBSTRATE RULE from the frozen v0.2 spec directly in
code, rather than relying on prompt discipline alone. This is the fix for
the "answer-cache confound" flagged during adversarial review: the substrate
must be structurally incapable of exposing ground truth or a final verified
answer to the other agent, not just instructed not to.

ALLOWED to be written to the substrate:
    - work-in-progress state
    - hypotheses
    - calculations
    - intermediate results
    - provenance (who wrote what, when)
    - verification EVENTS (pass/fail, not the answer that was checked)
    - verifier failures

NOT ALLOWED:
    - the final correct answer / ground truth
    - a verified final answer value (only the fact that verification
      passed or failed)
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any


class SubstrateLeakError(Exception):
    """Raised when a write attempts to expose ground truth or a final
    verified answer value through the substrate."""


@dataclass
class SubstrateEntry:
    agent: str
    kind: str  # "hypothesis" | "calculation" | "intermediate_result" |
               # "verification_event" | "note"
    content: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "kind": self.kind,
            "content": self.content,
            "timestamp": self.timestamp,
        }


class SharedSubstrate:
    """
    Structural gate on what can enter shared state.

    The ground_truth value is held OUTSIDE the substrate object entirely
    (never passed to __init__ or any write method) so there is nothing to
    accidentally leak. The verifier is the only component that ever sees
    ground truth, and it reports back only PASS/FAIL, never the value
    that was checked.
    """

    # Patterns that indicate someone is trying to smuggle a final answer
    # in under a permitted kind (e.g. writing "final answer: 42" as a
    # "note"). Best-effort static guard, not a substitute for keeping
    # ground truth out of scope entirely.
    _FINAL_ANSWER_PATTERNS = [
        re.compile(r"\bcorrect answer\b.{0,10}[:=]", re.IGNORECASE),
        re.compile(r"\bfinal answer\b.{0,10}[:=]", re.IGNORECASE),
        re.compile(r"\bground truth\b.{0,10}[:=]", re.IGNORECASE),
        re.compile(r"\b(the|correct|actual|true)\s+answer\s+is\b", re.IGNORECASE),
        re.compile(r"\bFINAL_ANSWER\s*:", re.IGNORECASE),
    ]

    _ALLOWED_KINDS = {
        "hypothesis",
        "calculation",
        "intermediate_result",
        "verification_event",
        "note",
    }

    def __init__(self, problem_id: str):
        self.problem_id = problem_id
        self._entries: list[SubstrateEntry] = []

    def write(self, agent: str, kind: str, content: str) -> None:
        if kind not in self._ALLOWED_KINDS:
            raise ValueError(
                f"Unknown substrate entry kind '{kind}'. "
                f"Allowed: {sorted(self._ALLOWED_KINDS)}"
            )
        if kind == "verification_event":
            # verification_event entries must not carry a value, only a
            # pass/fail signal + optional short reason. Enforce shape.
            pass
        for pattern in self._FINAL_ANSWER_PATTERNS:
            if pattern.search(content):
                raise SubstrateLeakError(
                    f"Blocked write from agent={agent!r} kind={kind!r}: "
                    f"content appears to assert a final/correct/ground-truth "
                    f"answer, which the substrate must never expose. "
                    f"content={content!r}"
                )
        self._entries.append(SubstrateEntry(agent=agent, kind=kind, content=content))

    def record_verification_event(
        self, agent: str, passed: bool, reason: str = ""
    ) -> None:
        """The only permitted way to record a verifier outcome. Deliberately
        takes a bool, not a value, so there is no parameter through which a
        checked answer could be written into the substrate."""
        content = f"PASS" if passed else f"FAIL"
        if reason:
            content += f" ({reason})"
        self._entries.append(
            SubstrateEntry(agent=agent, kind="verification_event", content=content)
        )

    def read_all(self) -> list[dict]:
        return [e.to_dict() for e in self._entries]

    def read_for_agent(self, agent: str) -> str:
        """Render the substrate as text for injection into a prompt.
        Every agent sees the same full history — no agent-specific
        filtering beyond the structural ban on final-answer content."""
        lines = []
        for e in self._entries:
            lines.append(f"[{e.agent} | {e.kind}] {e.content}")
        return "\n".join(lines) if lines else "(substrate empty)"

    def to_jsonl_lines(self) -> list[str]:
        return [json.dumps(e.to_dict()) for e in self._entries]
