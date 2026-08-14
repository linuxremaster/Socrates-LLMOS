# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
§5 TASK SET.

These 10 problems are a STARTING PLACEHOLDER, not the frozen set — you must
review and freeze the actual set yourself before running real trials, per
§5 "Freeze the task set before experimental runs. Do not modify failed
problems after seeing results." I generated these to the spec's
requirements (deterministic ground truth, auto-verifiable, no external
factual knowledge, multi-step) but freezing is a decision only you should
make, since the spec explicitly assigns that authority to the human.

Once you've reviewed/edited this list, treat it as immutable for the pilot.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    problem_id: str
    prompt: str
    ground_truth: str  # sympy-parseable expression


TASKS: list[Task] = [
    Task(
        "P01",
        "A train travels 60 mph for 2 hours, then 45 mph for 3 hours. "
        "What is its average speed in mph for the whole trip? "
        "Answer as a fraction or decimal.",
        "255/5",
    ),
    Task(
        "P02",
        "Twice a number, minus 7, equals 3 times the number minus 15. "
        "What is the number?",
        "8",
    ),
    Task(
        "P03",
        "A rectangle's length is 4 more than its width. Its area is 96. "
        "What is the width?",
        "8",
    ),
    Task(
        "P04",
        "A tank is filled by pipe A in 6 hours and pipe B in 3 hours. "
        "If both pipes run together, how many hours to fill the tank? "
        "Answer as a fraction.",
        "2",
    ),
    Task(
        "P05",
        "The sum of three consecutive integers is 72. What is the "
        "largest of the three?",
        "25",
    ),
    Task(
        "P06",
        "A store marks up an item 25% then offers a 20% discount on the "
        "marked-up price. If the original price was 80, what is the "
        "final price?",
        "80",
    ),
    Task(
        "P07",
        "Solve for x: 3(x - 2) + 5 = 2(x + 4) - 3",
        "6",
    ),
    Task(
        "P08",
        "A car depreciates 15% per year. After 2 years, a car originally "
        "worth 20000 is worth how much? Round to nearest whole number.",
        "14450",
    ),
    Task(
        "P09",
        "Two numbers have a sum of 45 and a difference of 11. What is "
        "the larger number?",
        "28",
    ),
    Task(
        "P10",
        "A recipe requires a ratio of 3 parts flour to 2 parts sugar. If "
        "15 cups of flour are used, how many cups of sugar are needed?",
        "10",
    ),
]

assert len(TASKS) == 10, "§4 pilot size requires exactly 10 problems"
assert len({t.problem_id for t in TASKS}) == 10, "problem_ids must be unique"
