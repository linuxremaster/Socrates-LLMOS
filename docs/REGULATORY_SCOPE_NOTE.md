<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Regulatory Scope Note

**Not legal advice.** This is factual context, checked against current
sources as of 2026-08-16, written by an AI instance, not a lawyer. Real
legal review is required before any use beyond personal/household
scope — see "Trigger conditions" below for exactly when that becomes
necessary, not optional.

## What this project actually is, for regulatory purposes

`socrates_llmos` (kernel + toolkit) and `relay_console` do not train,
fine-tune, or provide a general-purpose AI model. They orchestrate
calls to already-existing, already-regulated third-party models
(Claude, GPT, Gemini) via those providers' own official APIs. That
makes this project, at most, a **deployer/integrator** of GPAI
systems — not a GPAI model provider. Anthropic, OpenAI, and Google
carry the model-provider obligations; this project doesn't duplicate
them.

## Current framework status (verified 2026-08-16, re-check before relying on it)

**EU AI Act:** GPAI *model provider* obligations (Article 53) took
effect August 2025; enforcement began August 2, 2026. These apply to
the companies providing Claude/GPT/Gemini, not to a tool built on top
of their APIs. Deployer-level obligations under the Act generally
center on **high-risk use cases** — none of which this project
currently performs.

**US:** no comprehensive federal AI statute. Binding obligations sit in
a state-law patchwork — most relevantly, laws like Colorado's SB 26-189
targeting **automated decision-making technology that materially
influences consequential decisions** (employment, healthcare, housing,
credit, insurance, legal services). This project doesn't make
consequential decisions about real people in any of those categories.

## Trigger conditions — real legal review becomes necessary, not optional, the moment any of these become true

- This project (or `relay_console`, or any derivative) is used to make
  or materially influence a **consequential decision** about a real
  person — employment, healthcare, housing, credit, insurance,
  education, or legal services.
- The project is **monetized** or offered as a paid product/service —
  this alone changes the EU open-source exemption calculus.
- Distribution moves beyond personal/household use toward a broader
  user base, especially if any of those users are in the EU or a US
  state with active AI legislation (currently most actively: CA, CO,
  IL, TX, UT — re-check, this list changes).
- The hardened/at-risk-user line of work discussed earlier (and
  currently on hold) becomes active — that context has categorically
  different stakes and almost certainly different obligations.

## What to actually do if a trigger condition is met

Stop, and get real legal counsel before proceeding — this document is
a scope note, not a substitute for that review. The regulatory
landscape here (US state patchwork especially) has changed materially
multiple times within 2026 alone; treat any specific fact in this file
as needing re-verification before being relied on, not as settled.

**End Regulatory Scope Note**
