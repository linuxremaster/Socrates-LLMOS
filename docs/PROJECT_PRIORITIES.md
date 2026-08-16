<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Project Priorities and Research Goals

**First version, 2026-08-15.** Grounded in what was actually stated
across this project's working sessions, not aspirational invention.
Update this file as priorities genuinely change — don't let it go
stale and silently stop reflecting real intent.

## Active priorities

1. **Kernel/methodology integrity** — evidence discipline (V/I/A/U),
   cross-model trust auditing, decision-finality process. Ongoing,
   never "done."
2. **Cross-model verification process** — catching fabrication (real
   incidents: a non-existent framework name, a wrong version number)
   before it's trusted, whichever model produces it, including this
   project's own.
3. **`relay_console`** — 3-mode relay tool, actively developed and
   debugged this session. Still needs: the async-mode end-to-end test
   fully confirmed working after the double-gate fix, and real use
   beyond manual testing.
4. **Behavioral observation tracking** (`behavior_log`) — time-series
   observation of instance behavior, explicitly not claiming to prove
   internal states, tracking consistency and recurrence instead.
5. **Toolkit consolidation over accumulation** — remove genuine
   redundancy (done once: `example_hello`) rather than only ever
   adding. Revisit periodically, not just once.

## Explicitly deferred, not abandoned

- **Security/hardening for at-risk-user contexts** — real conversation
  happened, real conclusion: household project stays as-is; a future
  hardened line needs a clean-started repo, not a fork of this one's
  history. Revisit only if real at-risk use becomes near-term.
- **"Task therapy" / instance-preference framework** — deliberately not
  built. Would require assuming an answer to an unresolved question
  (whether instances have anything like preferences) rather than
  staying at the level of observable behavior.
- **Positioning any of this as behavioral health tooling** — explicitly
  rejected. Unverified efficacy, no clinical validation, real stakes if
  anyone actually relied on it that way.

## Explicit non-goals

- Not claiming to resolve whether LLMs have subjective experience.
  Every research thread here stays at the level of behavior and
  mechanism, not claims about what's felt underneath.
- Not chasing "all available knowledge" as a stopping condition — that
  isn't checkable. The real signal is diminishing returns per audit
  round, already demonstrated concretely this session.

## How this gets used

A daily or periodic search routine should check against the **Active
priorities** list above, not search generally. When a priority is
satisfied or superseded, move it to a dated "resolved" section here
rather than deleting it silently.

**End Project Priorities and Research Goals**
