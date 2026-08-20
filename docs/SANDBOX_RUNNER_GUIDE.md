<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Sandbox Runner Guide

*Originally conceived as a conflict resolution management system; became this epistemic-discipline kernel and toolkit for LLM work through a real redirection -- see `docs/PROJECT_PRIORITIES.md`'s Origin and Scope Evolution section.*

Real, working guardrails for running experimental, untrusted, or
LLM-suggested code — **not container-grade isolation**. Read the
scope section before relying on this for anything security-sensitive.

## Honest scope — what this is, and isn't

Docker, firejail, and bwrap were checked directly and confirmed
**unavailable** in the environment this was built in, and are unlikely
to be available in Termux either — Android restricts unprivileged
kernel namespace creation more than a typical Linux host does. Full
isolation (a real security boundary against a malicious or
deliberately escaping process) is **not** what this provides.

What it actually, genuinely provides — each one tested with a real
reproduction, not assumed:

- **CPU time limit**, via `resource.setrlimit(RLIMIT_CPU, ...)`. A
  genuinely infinite loop gets killed (SIGKILL) at the configured
  second count. Tested directly: a real `while True: x += 1` script
  was confirmed killed at exactly the configured limit.
- **Memory limit**, via `resource.setrlimit(RLIMIT_AS, ...)`. A
  genuinely unbounded allocator hits a real `MemoryError` at the
  configured limit. Tested directly with a real 10MB-chunk allocation
  loop.
- **No inherited credentials.** The subprocess runs with a stripped
  environment (`PATH` and `HOME` only) — even code that tries to reach
  the network has nothing to authenticate with. Tested directly: a
  real environment variable set in the parent process was confirmed
  invisible inside the sandboxed subprocess.
- **A disposable, timestamped working directory**, wiped on
  `sandbox-reset`. Containment by discipline, not kernel enforcement —
  a sufficiently determined process could still reach outside via
  absolute paths. This stops accidents and casual missteps, not a
  deliberate attack.

**What this does NOT protect against:** a process that deliberately
tries to read or write files outside its working directory via
absolute paths; a process that has some other way to reach the
network despite missing credentials; any kernel-level exploit. If a
real security boundary against a malicious or adversarial process is
ever actually needed, this is the wrong tool — that would need genuine
containers or VMs, which this environment doesn't currently support.

## How to use it

Run a script under sandbox limits:
```
llmos sandbox-run <script.py> [--cpu-seconds 10] [--memory-mb 256]
```
Defaults: 10 seconds CPU, 256MB memory. Adjust per what the script
actually needs — tighter limits catch runaway behavior faster.

List past runs, most recent first:
```
llmos sandbox-list
```

Wipe all sandbox run history clean (only ever touches
`state/sandbox_runs/`, never the real project):
```
llmos sandbox-reset
```

## Ties into the quarantine boundary

A sandboxed run's result is **not** auto-logged to the real ledger.
If a result is worth recording — say, from a manually-supervised
agentic experiment (see `KERNEL_ADOPTION_TRACKING.md` and A15's
"manually-supervised" framing) — log it explicitly:
```
llmos propose-observation "<instance>" "<subject>" "<category>" low "<what happened>" --experiment-id "<id>"
llmos approve-pending 0
```
Same real human-approval gate as everything else logged this way —
running code in the sandbox doesn't bypass it.

## Full result detail

Each run writes `state/sandbox_runs/<run_id>/result.json` with the
exit code, whether it timed out, and captured stdout/stderr (capped at
4000 characters each, so a runaway print loop can't flood the file).
