<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# How to Use the Toolkit — No CLI Experience Required

*Originally conceived as a conflict resolution management system; became this epistemic-discipline kernel and toolkit for LLM work through a real redirection -- see `docs/PROJECT_PRIORITIES.md`'s Origin and Scope Evolution section.*

If you've never typed a command into a terminal before, start here.

**Step 1: Open a terminal.** On Windows that's PowerShell or Command
Prompt; on Mac or Linux it's called Terminal; on Android via Termux,
it's the Termux app itself.

**Step 2: Install it.** Replace the path below with wherever you
actually put the `socrates_llmos` folder:

```
cd /path/to/socrates_llmos
pip install -e . --break-system-packages --no-build-isolation
```

**Step 3: Ask it what it can do.**

```
llmos --list-commands
```

You'll get a list like this (shortened):

```
check-dir       compares two folders and tells you what grew
drift-check     checks text against rules you've written
flag-claims     flags suspicious-sounding sentences for a human to check
audit-all       the main "is everything okay" check, see below
session-close   run this at the end of a working session
rag-query       searches your own files for a topic
```

**Step 4: Try the main one.**

```
llmos audit-all
```

If the kernel file has never been "pinned" before, it'll tell you to
run `pin-kernel` first — that's normal for a first run, it just means
"I don't have a saved copy to compare against yet." Do what it says,
then run `audit-all` again.

**What "PASS" and "FAIL" actually mean here:** PASS means the file
matches exactly what you told the tool to trust, and nothing about its
structure looks broken. FAIL means something changed — which might be
completely fine (you edited it on purpose) or might be worth a second
look (you didn't). The tool doesn't know which; it just tells you
*that* something changed, clearly, so you can decide.

**Every command works the same basic way:**
```
llmos <command-name> <the file or folder it applies to> [optional extra flags]
```
Add `--help` after any command name to see its specific options, e.g.:
```
llmos rag-query --help
```

**When you're done for the session, run:**
```
llmos session-close
```
This re-indexes everything, checks for drift, saves your progress to
git, and tidies up old log entries — all in one command, so you don't
have to remember five separate steps.

**You will not break anything by experimenting.** Every tool here reads
files and writes small log files — none of them delete or overwrite
your actual work without you explicitly telling them to.

— Socrates LLMOS
