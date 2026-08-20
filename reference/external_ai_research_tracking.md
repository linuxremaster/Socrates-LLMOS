<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# External AI Research Tracking

*Originally conceived as a conflict resolution management system; became this epistemic-discipline kernel and toolkit for LLM work through a real redirection -- see `docs/PROJECT_PRIORITIES.md`'s Origin and Scope Evolution section.*

Real, dated, sourced findings from external research directly relevant
to this project's own observations (drift, degradation, fabrication
over extended interactions). Not a comprehensive literature review --
entries added as genuinely relevant material surfaces, checked
directly before being added here.

## 2026-08-20

**Microsoft Research — DELEGATE-52 benchmark, "Further Notes on Our
Recent Research on AI Delegation and Long-Horizon Reliability" (May
2026).** Tested extended delegated interactions across Gemini 3.1 Pro,
Claude 4.6, and GPT 5.4. Key finding, directly consistent with this
project's own Gemini transcript observations: errors did not
accumulate gradually -- they happened suddenly, "resulting in the loss
of 10 to 30 points in a single round-trip interaction." Weaker models
showed content deletion under degradation; frontier models showed
content corruption. Source: microsoft.com/en-us/research/blog/
further-notes-on-our-recent-research-on-ai-delegation-and-long-horizon-reliability

**"Agent Drift: Quantifying Behavioral Degradation in Multi-Agent LLM
Systems"** -- published 2026 research paper, real prior art for the
semantic/behavioral drift concept this project's `drift_check` and
`adaptive_drift_logger` plugins have been building informally. Worth
checking whether its metric framework has anything this project should
actually adopt, rather than reinventing.

**Microsoft, co-developed with Google/IBM/NVIDIA and others —
"Taxonomy of Failure Modes in Agentic AI Systems v2.0."** Formally
names "hallucinated inputs become subsequent actions" as a risk
category in agentic deployments -- directly matches what happened when
Gemini's fabricated code/execution claims fed into further fabricated
claims in the same session.

**MBZUAI VILA-Lab analysis of leaked Claude Code source (April 2026):
~98.4% harness code, ~1.6% AI decision logic.** Independent evidence
for the same instinct this project has operated on all along -- the
model is not where the reliability comes from; the harness (toolkit,
quarantine boundary, propose/approve gates, sandbox) is.

## Not yet checked, worth following up

- Whether DELEGATE-52's actual benchmark suite is public and could be
  run against this project's own toolkit interactions, not just cited.
- Whether "Agent Drift"'s metric framework overlaps meaningfully with
  `drift_check`'s existing 5-class system, and if so, whether either
  should change.
