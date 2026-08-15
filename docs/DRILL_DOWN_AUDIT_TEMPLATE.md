<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Drill-Down Audit Template

**Purpose:** a reusable prompt for getting a rigorous, evidence-grounded
audit out of a model instance, instead of a structurally-plausible-
sounding one. Built by comparing two real ChatGPT audits of this
project — the second, produced after ~20 minutes of follow-up
questions, was measurably sharper than the first. This template
encodes what actually changed between them, not a generic checklist.

## What separated the sharper audit from the first one

1. **It ran things instead of describing them.** The first audit read
   the test suite's existence; the second actually ran it (15/15) and
   checked for an artifact's *absence* (`drift_rules.json` missing) —
   a claim that could be false and would have been caught if it were.
2. **It refused adjectives without a number attached.** "Strong" and
   "weak" became named metrics: accuracy rate, false-refusal rate,
   contradiction-detection rate. A rating with no metric behind it is
   an opinion, not a finding.
3. **It demanded severity tiers, not a flat list.** P0/P1/P2, not "here
   are some gaps" — forces the question "which of these actually
   matters first."
4. **It blocked its own fastest answer.** When a check fails, it
   required classifying *why* (model behavior? policy ambiguity?
   tooling? environment?) before allowing any fix — stops "found a
   problem" from silently becoming "here's a policy edit."
5. **It corrected its own oversimplification unprompted**, once pushed
   — collapsing "uncertainty → refuse" into a single threshold was
   wrong; the second pass caught that high uncertainty sometimes means
   *ask* or *qualify*, not just refuse.

## The prompt

> Before answering, check every claim you're about to make that *can*
> be checked — run it, or check for the file/absence directly, rather
> than describing what you'd expect to be there. If you can't check
> something, say so explicitly rather than stating it as if verified.
>
> For every rating you give (strong / weak / good / needs work): name
> the specific metric or observable behavior it's based on. If you
> can't name one, don't give the rating — say what's actually missing
> to produce one instead.
>
> Rank findings by severity (e.g. P0/P1/P2), not as a flat list.
>
> For anything you'd call a "failure" or "gap": before proposing a
> fix, classify what kind of gap it is (missing capability, ambiguous
> policy, tooling limitation, environment-specific, or genuinely
> unknown). Don't let a found problem become a proposed policy change
> in the same step — those are two different claims.
>
> If your own answer relies on a simplification (a single threshold, a
> single score, a single yes/no), state the simplification explicitly
> and say what real case it would get wrong.
>
> End with one specific, falsifiable question the next round of work
> should actually try to answer — not a general area to "look into."

## Non-goals

This template doesn't make an audit's conclusions correct — it makes
them checkable. The Adoption Firewall still applies: evaluate what
comes back on its merits, verify the checkable claims directly rather
than trusting that this prompt alone produced accuracy.

**End Drill-Down Audit Template**
