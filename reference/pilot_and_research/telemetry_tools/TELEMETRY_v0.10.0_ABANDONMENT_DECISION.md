<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Telemetry Canvas: v0.10.0-alpha abandoned, v0.9.1-alpha is the successor

**2026-08-29. Real engineering decision, documented here because it
previously existed only in conversation — a future instance had no
durable way to verify it without this file.**

## What happened

`v0.10.0-alpha` ("kernel-optional") was intended to be a small, targeted
change to `v0.9.0-alpha`: replace the hardcoded kernel constant with an
optional file upload, nothing else. What actually shipped was a
near-total rewrite — a direct function-level diff found only 9
functions in v0.10.0 against 32 in v0.9.0, with almost no name overlap.

**Confirmed lost in the rewrite, not a deliberate simplification:**
- Hash-chaining and tamper-evidence (`appendEvent`'s `previous_hash`
  linkage, `verifyChain()`) — every event in v0.10.0 gets an
  independent hash with no linkage to the one before it. A stored JSON
  file could be reordered, have entries deleted, or have entries
  inserted, and nothing would detect it.
- The entire self-test suite (`runSelfTests` and everything it
  covered) — gone. v0.10.0 has no self-tests at all.
- Surface detection (`analyzeAndLog`, `analyzeWorkflowResponse`, and
  the deterministic lexical pattern-matching they implemented) — gone.
  A genuine v0.10.0-produced report confirmed this directly: 0 mentions
  of "surface detection," "self-certification," or any related term
  anywhere in the file. The tool no longer flags anything automatically.

This was confirmed as accidental drift, not an intentional redesign,
by the person operating the tool across both versions.

## What was done instead

Rather than reconstruct ~32 functions' worth of dropped logic inside
v0.10.0's different architecture, `v0.9.1-alpha` was built the other
way around: start from `v0.9.0-alpha` (proven across 6 real audit
runs, chaining and self-tests and detection all confirmed working),
and apply only the one actually-intended change.

**The actual diff, real and small:** the hardcoded `KERNEL_VERSION`/
`KERNEL_SHA256`/`KERNEL_PROMPT` constants became mutable state,
defaulting to unset; a file input and `loadKernelFile()` function were
added, following the exact pattern already used for the prompt
manifest loader; `QUEUE` construction was made conditional on whether
a kernel was actually loaded; four self-tests were adjusted to hold
correctly whether or not a kernel is present, plus one new test added
(confirming the queue has no phantom kernel entry when none is loaded).
Everything else — chaining, detection, validation, export/import — is
untouched v0.9.0 code.

**Real regression caught and fixed during this process, not by code
review alone:** making `QUEUE` start empty broke `renderPrompt()` on
page load (`QUEUE[0]` was previously always safe since a kernel was
always present at index 0). Found by actually executing the code in a
Node harness with mocked browser APIs, not by reading the source.
Fixed, then re-tested.

**Verified directly, by execution, not just review:**
- Loading a kernel, then a *different* kernel, correctly replaces it —
  no duplicate or stale kernel entry in the queue.
- Hash-chaining still works: 3 real events appended, chain verified
  valid; one event's content then deliberately corrupted, and
  `verifyChain()` correctly detected the tamper at the right index
  with the right reason.
- All self-tests pass in both configurations (kernel loaded / no
  kernel loaded).

## Current status

**Update, 2026-08-29: superseded by v0.9.2-alpha, real functional
update not merely cosmetic despite being introduced that way.** Real,
tested changes: `prompt_number` now travels as data on each queue item
instead of being inferred from array position -- this fixes a genuine
latent bug in v0.9.1 where the *displayed* prompt number would shift
depending on whether a kernel was loaded (since v0.9.1 used raw array
index). Also added: real host/model-agnostic generalization (a real
`<select>` replacing hardcoded "Gemini Web"), backward-compatible
storage-key migration for existing v0.8-lineage ledgers, and an
automatic `condition: KERNEL_OPTIONAL/KERNELLESS` field recorded from
actual observed state rather than an operator-selected label. All
verified by direct execution in a Node harness (self-tests, hash-chain
append/verify, kernel load/swap, `buildEvaluationPackage`, and the
storage migration itself), not by code review alone. SHA-256
`1812b678c1b5b5560a4004c92167b6d8358ea9a82fd6bfd410ff456938219c62`.

**Both files preserved here, real SHA-256 for direct verification:**
- `../Socrates_Telemetry_Canvas_v0.9.2-alpha.html` — active lineage.
- `../Socrates_Telemetry_Canvas_v0.9.1-alpha_kernel-optional.html` —
  `1967c9e6752bce8b0ba0fc7f3affee1bc7342361dbd5e48d58d9bf30b34e7c53`
  — superseded, preserved as real history, not deleted.
- `abandoned/Socrates_Telemetry_Canvas_v0.10.0_kernel-optional.html` —
  `0599897916c5dda5418b4f8cb614edb7dd77c52774d12865375bfa386c09d604`
  — preserved, not deleted, explicitly not the successor to v0.9.0.

Supersession edge, stated precisely rather than implied by file
presence alone:

```
v0.9.0-alpha
    |-- v0.9.1-alpha   (superseded active lineage, targeted kernel-optional change)
    |     |-- v0.9.2-alpha  (current active lineage, prompt-numbering + model-agnostic fixes)
    |-- v0.10.0-alpha  (abandoned experimental branch, accidental near-rewrite)
```

`v0.10.0-alpha` is not deleted specifically so a future instance can
diff it directly against v0.9.1 rather than trust this note's
characterization alone.

`v0.9.1-alpha` is the active lineage. `v0.10.0-alpha` should be treated
as an abandoned branch — not deleted from history, but not the basis
for future work. Its only feature genuinely worth considering
separately, if wanted later, is an explicit `condition()` selector
(letting an operator pick a named test condition like `KERNELLESS`
rather than inferring it from whether a file was uploaded) — that
would need to be deliberately re-added to v0.9.1's architecture, not
inherited by reverting to v0.10.0.
