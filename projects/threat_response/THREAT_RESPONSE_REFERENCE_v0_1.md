<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Threat Response & Corrective Action Reference — v0.1 Draft

**Status: first draft, not reviewed by digital-security domain experts.**
The classification logic and general guidance are sound; specific contact
details should be re-verified before this is relied on, and this document
should not be treated as legal or safety advice for a specific situation —
it's a starting reference, not a substitute for the organizations it points
to, who do this professionally.

## Purpose

When a threat is detected (malware, phishing, surveillance, targeted
attack, disinformation), the correct next step depends on **who the
person is and what "authorities" means in their context** — not on the
technical nature of the threat alone. The same detected threat can
require opposite responses depending on that context. This document
exists to make that branching decision explicit, rather than defaulting
to one answer for everyone.

---

## Step 0: Classify before recommending anything

Ask, in order:

1. **Is there any reason to think a government or state-linked actor
   could be the source of the threat, or could retaliate against the
   person for reporting it?** (Journalist, activist, dissident,
   human rights worker, member of a targeted minority, living under or
   working against an authoritarian government, prior surveillance/
   harassment.)
   - **If yes → go to Path B.** Do not recommend contacting local
     government channels. This is not a minor caveat — it can be the
     difference between getting help and creating direct danger.
   - **If no → continue.**

2. **Is this a technical security threat** (malware, phishing, account
   compromise, scam) **or an information/persuasion threat**
   (propaganda, disinformation, manipulative framing)?
   - Technical threat, no state-actor concern → **Path A**
   - Information/persuasion threat → **Path C**

When uncertain which applies, default to Path B's caution rather than
Path A's — the cost of being overly cautious with a safe channel is
small; the cost of routing an at-risk person to an unsafe one is not.

---

## Path A: Ordinary technical threat, no state-actor concern

Standard, safe guidance:

- **Isolate first.** Disconnect the affected device from the network
  before doing anything else, if malware or active compromise is
  suspected.
- **Don't reuse compromised credentials.** Change the password
  everywhere it was reused, not just on the affected account.
- **Preserve evidence before cleaning up** — screenshots, headers,
  timestamps — in case a report is filed later.
- **Report through official channels:**
  - US: **CISA** (report.cisa.gov) for general cyber incidents; **FBI
    IC3** (ic3.gov) for internet crime including malware and fraud.
  - EU: national CERT, or under NIS2 for covered entities, the
    designated national reporting authority.
  - Sector-specific: **FS-ISAC** (finance), **H-ISAC** (healthcare), or
    the relevant sector ISAC if applicable.
  - A specific product/vendor is involved: that vendor's PSIRT
    (product security incident response team) is often faster than a
    general government channel.
- **Sample sharing:** submitting a file hash to VirusTotal makes it
  visible to many security vendors at once without needing to contact
  each individually.

---

## Path B: Suspected state-linked targeting / authoritarian context

**Do NOT recommend contacting local government cybercrime or security
authorities as a first step.** If the state is a plausible source of
the threat, that channel is not neutral for this person.

Independent, vetted organizations built specifically for this:

- **Access Now Digital Security Helpline** — free, 24/7, real-time,
  responds within ~2 hours, built specifically for at-risk activists,
  journalists, and civil society. Contact: **help@accessnow.org**
  (verified current). Confidential by design.
- **EFF Surveillance Self-Defense** — practical, situation-specific
  security guidance (self-serve guide, not a helpline).
- **Citizen Lab** (University of Toronto) — research and direct
  assistance specifically on state-sponsored spyware and targeted
  surveillance.
- **Committee to Protect Journalists (CPJ)** and **Freedom of the
  Press Foundation** — for press-specific targeting.

**What NOT to do in this path:**

- Don't file a report that requires revealing identity to a state-linked
  channel.
- Don't assume a "national CERT" is safe by default — verify its
  independence from the state security apparatus for that specific
  country before treating it as neutral.
- Don't recommend actions that create a paper trail the person didn't
  choose to create.
- Don't guess at what's safe for a specific country's situation — that's
  precisely the judgment the organizations above specialize in and update
  as conditions change; a static document can go stale on this faster
  than almost anything else in it.

---

## Path C: Propaganda / disinformation exposure

This is not a "contact authorities" situation at all — it's an
information/reasoning problem, and treating it like a security incident
misframes it. This is what the depolarize prompt (`prompt.txt`) and the
cognitive-state-intervention design notes already address directly:

- The goal is improving the person's reasoning process, not reporting
  the content or changing their conclusion by force.
- No law-enforcement or state channel is appropriate here in the general
  case — this path exists mainly to make sure Path A/B instincts
  ("who do I report this to?") don't get misapplied to something that
  isn't a security incident.
- Platform-level reporting (flagging content to the hosting platform's
  own moderation system) is the closest analog to "reporting," where it
  exists — separate from anything in Path A or B.

---

## Cross-cutting: what not to do, regardless of path

- Don't let an automated detector make the classification in Step 0
  autonomously and route a report without human review — false
  positives here have real cost, and Path B's stakes make an
  automated misroute worse than a technical false positive elsewhere.
- Don't present this document's guidance as legal advice or as a
  guarantee of safety — it's a starting point for a human decision, not
  a replacement for one.
- Don't treat "we searched and found no evidence a channel is
  compromised" as proof it's safe — for Path B specifically, absence of
  evidence is genuinely weaker evidence than usual, given the nature of
  state surveillance.

---

## Verification status of sources in this document

- Access Now Digital Security Helpline contact (help@accessnow.org),
  24/7 availability, ~2 hour response time: confirmed via web search,
  current as of this document's drafting.
- CISA, FBI IC3, EFF SSD, Citizen Lab, CPJ, Freedom of the Press
  Foundation: named from general knowledge as established organizations
  in this space — their current contact details were not individually
  re-verified in this draft and should be checked before relying on
  them in a real situation.

**Next step if this becomes part of the toolkit:** review by someone
with actual digital-security-for-at-risk-populations expertise before
any plugin surfaces this content to a real user. This document is a
starting structure for that review, not a finished, authoritative
reference.
