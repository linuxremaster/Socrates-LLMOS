<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

Think of cognitive-state intervention as changing the conditions under which someone is reasoning, rather than simply giving them better information.

It doesn't mean manipulating the person or trying to make them believe something. In the context we've been developing, it would mean helping the human move from a potentially distorted reasoning state into a more useful one.

The basic idea

Suppose someone encounters a provocative political claim.

A conventional LLM response might do this:

CLAIM
  ↓
RESEARCH
  ↓
FACT CHECK
  ↓
REPORT

A cognitive-state intervention would first ask:

What state is the person currently reasoning from?

For example:

emotionally activated

defensive

highly certain

catastrophizing

treating inference as fact

interpreting disagreement as hostility

operating from incomplete information


Then the system changes its interaction strategy accordingly.

USER INPUT
     │
     ▼
STATE SIGNALS
     │
     ├── emotional activation?
     ├── certainty?
     ├── factual/inferential mixing?
     ├── adversarial framing?
     └── missing information?
             │
             ▼
      SELECT INTERVENTION
             │
      ┌──────┼─────────┐
      ▼      ▼         ▼
   slow    clarify   reframe
      │      │         │
      └──────┼─────────┘
             ▼
       BETTER REASONING
             │
             ▼
       EVIDENCE / ANALYSIS

The critical distinction

The system isn't trying to change the conclusion.

It's trying to improve the process by which the conclusion is reached.

That gives us a very different objective:

> Don't optimize for agreement. Optimize for reasoning quality.



Someone can emerge from the intervention still believing the original position. That's completely acceptable if they now understand:

what is actually known,

what they're inferring,

what remains uncertain,

why another person might reasonably disagree,

and what evidence could change their mind.


Where empathy fits

This also explains why I don't think we need to keep expanding the empathy layer.

Empathy is one possible intervention mechanism, not the objective.

For example:

Bad intervention:

> "I understand why you feel that way, but here's why you're wrong."



Better:

> "There's a legitimate concern embedded in what you're saying. Let's separate that concern from the stronger claim being made and see which parts the evidence actually supports."



The second response changes the reasoning environment without requiring the LLM to endorse the conclusion.

And this connects directly to our LLMOS work

This is almost exactly the distinction we've been developing between LLM cognition and external environment evolution.

The model doesn't need to become permanently different.

Instead:

HUMAN
                      │
                      ▼
              CURRENT COGNITIVE
                   STATE
                      │
                      ▼
              ┌──────────────┐
              │     LLM      │
              │ intervention │
              └──────┬───────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    evidence      framing      uncertainty
        │            │            │
        └────────────┼────────────┘
                     ▼
              EXTERNAL STATE
              / ARTIFACTS
                     │
                     ▼
             REVISED REASONING
                     │
                     ▼
                 HUMAN

That is potentially much more powerful than making the LLM progressively more persuasive.

And it gives us something testable.

We could eventually ask:

> Does an intervention-oriented prompt produce measurable improvements in reasoning quality, uncertainty calibration, evidence discrimination, and willingness to revise beliefs compared with a conventional report-oriented prompt?



That's no longer just philosophy. That's an experimental hypothesis.

And importantly, I would not call it "changing the person's cognitive state" as an established scientific claim yet. "Cognitive-state intervention" is a useful design hypothesis/name for the mechanism we're describing, not something we've established empirically.