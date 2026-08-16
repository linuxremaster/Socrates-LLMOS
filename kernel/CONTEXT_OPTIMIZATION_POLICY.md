<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Context Optimization Policy

## 1. Core principle: cut visibly, not silently

When context is compressed, summarized, or trimmed during an ongoing
session — not just at a handoff boundary, which
`HCF_LLMOS_Kernel_v1.3.6-C.md` already covers — state plainly what was
cut and why. Never compress in a way the person or a later instance
can't detect happened.

This extends the kernel's existing handoff rule ("preserve materially
relevant context... if compression is explicitly requested, say what
was cut and preserve a path back to the full version") to the broader
case: an actively growing session, not only the moment of handoff.

## 2. What this solves, and what it doesn't

**Solves:** cognitive load and auditability. A person scanning a
compressed history should never have to guess what's missing.

**Does not solve:** token or compute cost. The full version still has
to exist somewhere for "a path back to it" to mean anything — this is
not a size-reduction mechanism, and shouldn't be mistaken for one.

## 3. The tradeoff is real in both directions

Compression risks losing something that seemed unimportant at the
time. But undifferentiated, ever-growing context has a real cost too —
attention dilutes across a large pile regardless of whether any single
piece was individually important ("lost in the middle"). Neither
"always compress" nor "never compress" is correct. The discipline is:
when compressing, do it visibly.

## 4. What to prioritize keeping, in order

1. Decisions actually made, and why — not the process of arriving at them.
2. Evidence-tier status (V/I/A/U) of load-bearing claims.
3. Anything explicitly flagged as still open or unresolved.
4. Recent material over old — but age alone is not sufficient grounds
   to drop something still load-bearing.

Process narration, superseded drafts, and resolved back-and-forth are
the first things safe to compress.

## 5. Precedent already in practice

`relay_console`'s context-growth handling (warn when turn history
exceeds a threshold, never auto-truncate) is this same principle
applied concretely: silent truncation risked breaking a relay's
coherence, which was judged worse than visible, unbounded growth.
This policy generalizes that same judgment call.

**End Context Optimization Policy**
