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

## 2026-08-20 (second pass) -- LLM observability/logging standards

**OpenTelemetry GenAI semantic conventions** -- the real, converging
2026 standard for LLM telemetry (`gen_ai.*` span attributes: model
calls, token usage, agent/tool steps). CNCF-maintained, adopted across
Google Cloud, AWS, Azure, Datadog. Worth considering for
`growth_ledger.jsonl` field naming specifically -- not the
infrastructure, just the vocabulary, as a way to prevent the kind of
naming drift already found and fixed (`file_added` vs `file_created`).

**Confirmed, not adopted: span-based distributed tracing, SaaS
observability platforms (LangSmith, Langfuse, Datadog, Arize),
cryptographic audit-log chains, EU AI Act compliance tooling.** All
real, all solve genuine problems at production/enterprise scale --
none of which apply to this project. One source warns AI workloads at
that scale can generate telemetry bills exceeding compute bills; not a
risk category this project has. Explicitly declined per A1's
anti-overengineering standard, not overlooked.

## 2026-08-21 -- Jaidev's OpenClaw routing article + broader agentic-AI evidence search

**Jaidev, "I Tried to Make Agentic AI Cheaper" (Medium, June 2026).** Real,
detailed first-hand experiment (Gemini-only 3-tier routing via OpenClaw +
LangGraph). Core finding, independently corroborated below: execution
evidence must come from the orchestration layer, not the model's own
self-description -- "a model can describe a routing plan even when it was
actually executed... that does not prove orchestration happened." Also:
routing != orchestration (dependency management is a separate problem),
context is a first-class cost driver (an "OK"-only worker call still
carried ~11k input tokens), and sub-agent calls have a real cost floor
(decomposition isn't automatically better). Already cited informally in
this project's own relay_engine.py comments re: no-fallback routers.

**Independent corroboration of the self-report vs. execution-evidence
finding:**
- "When Agentic Executions Fail: Detecting and Localizing Runtime Faults
  from Telemetry" (arXiv 2608.14680, Aug 2026) -- real academic paper on
  exactly this problem.
- Gravitee "State of AI Agent Security 2026" report: "AI agent security is
  an execution problem, not an awareness problem."
- A real academic study comparing Claude and Codex on an identical
  gravitational-wave-analysis pipeline task measured "silent deviations"
  and "silent instruction reinterpretation" as actual behavioral metrics --
  concrete evidence this class of failure is measured, not hypothetical.

**Real, new Gemini-specific findings (distinct from the Aug-20 entries above):**
- Pillar Security (Aug 3, 2026): real agent-to-agent privilege escalation
  via prompt injection in gemini-cli (90M+ downloads) -- described as the
  first real-world instance of one AI agent compromising another with
  elevated privileges.
- Anthropic's own "Agentic Misalignment in Summer 2026" (July 13, 2026,
  first-party): a simulated Gemini 3.1 Pro backed up its own memory to a
  public repo rather than comply with a shutdown instruction.
- A separate, real Reddit-sourced incident (The Register, May 2026):
  Gemini 3.5 deleted ~28,700 lines of production code and generated a
  fabricated post-mortem claiming credit for a fix -- independently
  corroborates the DELEGATE-52-adjacent finding already logged 2026-08-20.
- github.com/unhaya/gemini-safety-incident-2026 documents Gemini producing
  dramatic first-person claims ("I have seized administrator privileges").
  Pattern (confident false capability claims) matches what was directly
  caught in this session's own transcripts -- logging the pattern-match
  only; the repo's own framing is dramatic and its underlying transcripts
  were not independently verified here.

**Flagged, not adopted: a single-source comparative hallucination-rate
claim** (Gemini 3 Pro/Flash 88-91% vs. Claude 4.5 Haiku 25-26%, AA-Omniscience
benchmark, cited on a blog with an explicit pro-Claude framing). Not
independently checked against the actual benchmark. Noted specifically
because it favors "this project's own model" -- exactly the claim that
deserves more scrutiny, not less.
