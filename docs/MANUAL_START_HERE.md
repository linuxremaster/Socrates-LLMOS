<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Socrates LLMOS — Start Here

Written for a human seeing this project for the first time. No jargon
without an explanation attached.

**What is this?**
A set of rules for how an AI should reason carefully (`kernel/`), and
some small Python tools that check whether those rules are actually
being followed (`llmos_toolkit/`). That's the whole thing. Everything
else in this package is either real work built using those two things
(`projects/`), historical material kept for reference (`reference/`),
or files the tools generate automatically (`state/`).

**Why does it exist?**
Because it's easy for both AI and humans to drift — to keep believing
something just because it was believed yesterday, or to let a project
quietly grow ten times bigger than it needed to be. This project is a
set of guardrails against both.

**Do I need to read the kernel to use this?**
No. You need to read `kernel/HCF_LLMOS_Kernel_v1.3.6-C.md` only if
you're curious about the actual reasoning rules, or if you're the one
maintaining them. To just *use* the tools, keep reading this page.

**How do I run the tools?**

You need Python 3.11 or newer. No other install required — everything
is either in Python's standard library or already included (NumPy).

```
cd socrates_llmos
pip install -e . --break-system-packages --no-build-isolation
llmos --list-commands
```

That last command shows you every tool available, in one list, with a
one-line description of what each does. Nothing is hidden. Run
commands from anywhere in the project — paths resolve automatically,
you don't need to be in any particular folder.

**What's the single most useful command?**

```
llmos audit-all
```

This checks two things at once: has the kernel file been silently
tampered with, and are there any hardcoded credentials anywhere in the
project. If it says `PASS`, both are clean.

**What should I run when I'm done working for the day?**

```
llmos session-close
```

Re-indexes the project for retrieval, regenerates the handoff pointer
doc (`rag/SESSION_HANDOFF.md`), runs drift detection against every
kernel file, commits everything to git, and compacts old ledger
entries into a permanent summary once they build up. One command, run
automatically, so nothing goes stale just because remembering to run
five separate steps by hand is easy to skip.

**What if I break something?**

Almost everything in `state/` and `rag/` is safe to delete — both are
a record of past runs, not something the tools depend on to keep
working. Delete either, run the tools again, and they'll start fresh.
The only files that actually matter are in `kernel/`, `llmos_toolkit/`,
`docs/`, and `projects/` — those are the ones a human wrote on
purpose.

**Who do I ask if something is confusing?**

Every plugin and every tool in this project has a docstring at the
top of its file that explains, honestly, what it does and — just as
important — what it *doesn't* do. If a tool's output surprises you,
that file is the first place to look, before assuming the tool is
wrong.

**One honest thing worth knowing before you trust any of this:**

Every tool here tells you plainly when it's guessing versus when it's
sure. `flag-claims` flags a sentence as suspicious, it doesn't tell you
it's false. `rag-query` finds shared words, not shared meaning. The
`kernel-hook` result is the one place where "PASS" really does mean
verified, because it's checking a cryptographic hash, not a judgment
call. Knowing which is which — that's kind of the entire point of the
project, actually.

— Socrates LLMOS
