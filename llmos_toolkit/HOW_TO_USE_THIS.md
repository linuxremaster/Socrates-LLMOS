<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# How to Use the Toolkit — No CLI Experience Required

If you've never typed a command into a terminal before, start here.

**Step 1: Open a terminal.** On Windows that's PowerShell or Command
Prompt; on Mac or Linux it's called Terminal; on Android via Termux,
it's the Termux app itself.

**Step 2: Tell it where the project lives.** Replace the path below
with wherever you actually put the `llmos_project` folder:

```
export PYTHONPATH=/path/to/llmos_project
cd /path/to/llmos_project/state
```

(On Windows PowerShell, use `$env:PYTHONPATH="C:\path\to\llmos_project"`
instead of `export`.)

**Step 3: Ask it what it can do.**

```
python3 -m llmos_toolkit --list-commands
```

You'll get a list like this (shortened):

```
check-dir       compares two folders and tells you what grew
drift-check     checks text against rules you've written
flag-claims     flags suspicious-sounding sentences for a human to check
kernel-hook     the main "is everything okay" check, see below
rag-query       searches your own files for a topic
```

**Step 4: Try the main one.**

```
python3 -m llmos_toolkit kernel-hook ../kernel/HCF_LLMOS_Kernel_v1.3.6-C.md
```

If the kernel file has never been "pinned" before, it'll tell you to
run `pin-kernel` first — that's normal for a first run, it just means
"I don't have a saved copy to compare against yet." Do what it says,
then run `kernel-hook` again.

**What "PASS" and "FAIL" actually mean here:** PASS means the file
matches exactly what you told the tool to trust, and nothing about its
structure looks broken. FAIL means something changed — which might be
completely fine (you edited it on purpose) or might be worth a second
look (you didn't). The tool doesn't know which; it just tells you
*that* something changed, clearly, so you can decide.

**Every command works the same basic way:**
```
python3 -m llmos_toolkit <command-name> <the file or folder it applies to> [optional extra flags]
```
Add `--help` after any command name to see its specific options, e.g.:
```
python3 -m llmos_toolkit rag-query --help
```

**You will not break anything by experimenting.** Every tool here reads
files and writes small log files — none of them delete or overwrite
your actual work without you explicitly telling them to.

— Socrates LLMOS
