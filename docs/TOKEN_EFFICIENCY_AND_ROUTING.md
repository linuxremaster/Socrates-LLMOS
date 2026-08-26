<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Token Efficiency & Model Routing — v0.1

*Originally conceived as a conflict resolution management system; became this epistemic-discipline kernel and toolkit for LLM work through a real redirection -- see `docs/PROJECT_PRIORITIES.md`'s Origin and Scope Evolution section.*

**Status: narrow, implemented in part.** The `--token-metrics` field on
`log-observation` is real, tested code. The routing guidance below is
operational advice for whoever builds an orchestration layer -- it is
not something this project's own toolkit currently executes.

## Origin, and what was deliberately not adopted

A much larger proposal ("Token Miser / Minimum-Sufficient-State
Architecture") was reviewed and found substantially redundant with
existing kernel/spec content -- its core "transmit only minimum
sufficient state" model already exists as A4's compression-preservation,
its compression-safety list already exists near-verbatim as "history is
immutable, attention is compressible" in `docs/
LLMOS_LEDGER_SECURITY_SPEC.md`, and its context-hygiene section
explicitly acknowledged the overlap itself. That proposal also assumed
a mechanism -- a client or orchestrator deciding what context to
transmit each turn -- that a chat-interface instance doesn't control;
the full conversation history arrives automatically, not by choice.
That assumption doesn't hold for every participant, which is part of
why this stayed narrow rather than becoming a kernel invariant.

Two pieces were genuinely new and are captured here, at the scope they
actually earned.

## Model routing (operational guidance, not toolkit-enforced)

Where an orchestration layer has the ability to choose which model
handles a given step, route by task requirement, not by uniformly
using the most capable available model:

```
low-cost/fast model   -> inventory, schema checks, extraction,
                          deterministic classification, routine
                          telemetry processing
stronger model         -> ambiguity, adjudication, architecture,
                          difficult calibration/reasoning
```

This is not a new idea -- it's consistent with real, already-logged
research (Jaidev's OpenClaw routing experiment, `reference/
external_ai_research_tracking.md`), which found routing by task
requirement effective while also finding that sub-agent calls have a
real cost floor (a trivial call still carries fixed overhead, so
routing "cheaper" isn't automatically routing "better"). Any future
orchestration work for this project should route with that finding in
mind, not decompose tasks more finely just because a cheaper model
exists for the pieces.

## Token-efficiency schema

`log-observation` and `propose-observation` accept `--token-metrics`,
a JSON object with a deliberately narrow, validated field set:

```
{
  "input_tokens": <non-negative integer>,
  "output_tokens": <non-negative integer>,
  "cached_tokens": <non-negative integer>,
  "files_opened": <non-negative integer>
}
```

Any other key is rejected, not silently accepted -- invalid input
fails cleanly with no ledger write, confirmed by direct testing.

**Deliberately excluded: a computed "useful-result-per-token" quality
proxy**, part of the original proposal's field list. That requires a
subjective judgment about output quality, not a raw, objectively
countable number -- exactly the kind of thing this project's evidence
tiers (A3) require being tagged as INFERRED or ASSUMED, not baked
silently into a schema as if it were a fact. If a quality-adjusted
metric is ever genuinely needed, it should be a separate, explicitly
tagged judgment recorded through the normal observation/evidence
pipeline -- not smuggled into what's supposed to be a raw-counts
schema.
