<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# What This Is Built On

Read this before using anything in this repository. It's short on
purpose.

## This project cannot enforce ethics. The providers can, and do.

Nothing in this kernel, this toolkit, or `relay_console` can stop
someone from misusing them — text in a repository has no enforcement
power over what someone does with their own copy. That's a real limit,
stated plainly, not a gap this document pretends to close.

What actually has teeth: **every call this project makes to Claude,
GPT, or Gemini runs through a real API key, tied to a real account,
with a real provider that enforces its own policy independently of
anything written here.** Using this project to violate a provider's
Usage Policy doesn't route around that provider's enforcement — it's
still your account, still their terms, still their consequence.

## The documents that actually bind you (verified 2026-08-16, re-check before relying on them)

- **Anthropic Usage Policy** — https://www.anthropic.com/aup
- **OpenAI Usage Policies** — https://openai.com/policies/usage-policies
- **Google Generative AI Prohibited Use Policy** — https://policies.google.com/terms/generative-ai/use-policy

These govern what you can do with the API keys you provide to
`relay_console` yourself. They are not this project's policies — they
are the actual providers' binding terms, independent of this repo.

## The frontier safety frameworks (context, not something that binds you directly)

These govern each lab's own decisions about training and deploying
their models — not your obligations as a user. Named here for context,
not as something enforceable against anyone using this project:

- **Anthropic Responsible Scaling Policy** (v3.1, effective 2026-04-02)
  — https://www.anthropic.com/responsible-scaling-policy
- **OpenAI Preparedness Framework** (v2, 2025-04-15)
  — https://openai.com/global-affairs/our-approach-to-frontier-risk/
- **Google DeepMind Frontier Safety Framework** (v3.0, 2026-04-17)
  — https://deepmind.google/discover/blog/introducing-the-frontier-safety-framework/

**Honest limit on all three:** these are voluntary, lab-authored
commitments, not external law — independent analysis has noted real
gaps (e.g. one academic review found OpenAI's framework *requests*
evaluation of some risks without *demanding* it for any). Worth
knowing rather than treating any of these as an ironclad guarantee.

## What this project adds on top of that

`docs/REGULATORY_SCOPE_NOTE.md` documents this project's own current
regulatory scope (EU AI Act, US state law) and explicit trigger
conditions for when real legal review becomes necessary.
`llmos_toolkit`'s `audit-all` command visibly flags if either that file
or `docs/LLMOS_SCOPE_AND_BOUNDARIES.md` goes missing — advisory only,
never blocking, never destructive. Deleting either doesn't break
anything and isn't punished. It just means the warning fires, honestly,
every time — the same way it would if you'd never read this file at all.

**End What This Is Built On**
