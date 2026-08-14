# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Implements §13 LOGGING from the frozen v0.2 spec:
    condition, model, prompt_version, timestamp, input/output tokens where
    available, model calls, substrate state changes, verifier results,
    final answer, PASS/FAIL, human intervention, error type.

Preserves raw outputs. Never overwrites — every run appends to
results.csv and state.jsonl, never truncates or rewrites prior rows.
"""

from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path


RESULTS_CSV_FIELDS = [
    "trial_id",
    "condition",
    "problem_id",
    "run_number",
    "model",
    "prompt_version",
    "timestamp",
    "input_tokens",
    "output_tokens",
    "model_calls",
    "verifier_calls",
    "submitted_answer",
    "pass_fail",
    "error_type",
    "human_intervention",
    "wall_clock_seconds",
]


@dataclass
class TrialRecord:
    trial_id: str
    condition: str
    problem_id: str
    run_number: int
    model: str
    prompt_version: str
    timestamp: float
    input_tokens: int | None
    output_tokens: int | None
    model_calls: int
    verifier_calls: int
    submitted_answer: str | None
    pass_fail: str  # "PASS" | "FAIL"
    error_type: str | None
    human_intervention: bool
    wall_clock_seconds: float


class PilotLogger:
    def __init__(self, output_dir: str = "./pilot_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_path = self.output_dir / "results.csv"
        self.state_path = self.output_dir / "state.jsonl"
        self._ensure_csv_header()

    def _ensure_csv_header(self) -> None:
        if not self.results_path.exists():
            with open(self.results_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=RESULTS_CSV_FIELDS)
                writer.writeheader()

    def log_trial(self, record: TrialRecord) -> None:
        with open(self.results_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=RESULTS_CSV_FIELDS)
            writer.writerow(asdict(record))

    def log_state_event(self, event: dict) -> None:
        """Append-only raw event log — substrate writes, human
        interventions, verifier calls, everything. Never overwritten."""
        event = {"logged_at": time.time(), **event}
        with open(self.state_path, "a") as f:
            f.write(json.dumps(event) + "\n")

    def log_human_intervention(self, trial_id: str, description: str) -> None:
        """§12/§15: any substantive human intervention must be recorded,
        not silently absorbed."""
        self.log_state_event(
            {
                "type": "human_intervention",
                "trial_id": trial_id,
                "description": description,
            }
        )
