<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# New User Test Guide

For someone trying this project for the first time. Each step has an
expected result — if you don't see it, stop there and ask before
continuing, don't assume it's fine.

## Before you start

You need Python 3.11 or newer. Nothing else to install manually —
everything the toolkit needs is either in Python's standard library or
already included.

## Step 1: Install

```
cd llmos_project
pip install -e . --break-system-packages --no-build-isolation
```

**Expected result:** ends with `Successfully installed llmos-toolkit-0.1.0`
and no red error text.

## Step 2: See what's available

```
llmos --list-commands
```

**Expected result:** a line saying `Discovered 13 plugin(s)`, followed
by a list of commands with a one-line description each.

## Step 3: Run the main health check

```
llmos audit-all
```

**Expected result:** two checks run — a secret scan and a kernel
integrity check. Secret scan should say `PASSED`. Kernel check may say
`FAILED: No kernel_pins.json` the very first time — that's normal, not
a bug. If it fails, run:

```
llmos pin-kernel kernel/HCF_LLMOS_Kernel_v1.3.6-C.md
llmos audit-all
```

**Expected result the second time:** both checks say `PASSED`, final
line reads `FINAL AUDIT STATUS: PASS`.

## Step 4: Read the kernel

Open `kernel/HCF_LLMOS_Kernel_v1.3.6-C.md` in any text editor. Read the
**Execution Boundary** section near the top.

**What to check:** it should say plainly that this is a document, not
a program, and that it doesn't create a runtime or override host
safety instructions. If that statement is missing or contradicted
anywhere, that's a real problem worth flagging before treating the
rest of the file as trustworthy.

## Step 5: Try retrieval

```
llmos rag-index kernel projects reference
llmos rag-query "evidence tiers"
```

**Expected result:** the index step reports a file count. The query
returns a ranked list of matching sections with scores — this is
keyword search, not meaning-based search, so results share vocabulary
with your query, not necessarily its intent.

## Step 6: Try the end-of-session command

```
llmos session-close --no-commit
```

`--no-commit` here is deliberate for a first test — it lets you see
what the command does without it touching git yet.

**Expected result:** four steps run in order — re-index, regenerate
`rag/SESSION_HANDOFF.md`, drift-check the kernel files, then a message
saying the commit step was skipped. Open `rag/SESSION_HANDOFF.md` and
confirm it lists real project files with recent timestamps.

## Step 7: Read the orientation sequence

Open `docs/INSTANCE_ORIENTATION_SEQUENCE.md`. This was written for a
new AI model instance adopting this project, but it's worth reading as
a human too — it's the same reasoning: read before deciding, check the
disclaimer is real, scan for actual risk rather than surface
vocabulary, state your scope before proceeding.

## If something doesn't match "expected result"

Don't assume you did something wrong. Check:
1. `docs/CHANGELOG.md` — has something changed recently that this
   guide hasn't caught up with yet?
2. The specific plugin's own docstring (top of its `plugin.py` file) —
   most say plainly what they do and don't do.
3. `docs/PROJECT_HANDOFF_SUMMARY.md` §6 — known open items, so you can
   tell a real problem from something already logged as unresolved.

**End New User Test Guide**
