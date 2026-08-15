<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Socrates LLMOS — Project Handoff Summary

**Purpose of this document:** a complete, standalone summary for picking
this project back up — in a fresh Claude conversation, handed to another
model, or just for your own reference later. Written to need no prior
context.

---

## 1. What this project actually is

Two things, kept deliberately separate:

- **`kernel/`** — a small set of behavioral rules for how an AI should
  reason: evidence tiers (Verified/Inferred/Assumed/Unknown), anti-drift
  discipline, anti-overengineering, non-defensiveness under criticism.
  Consolidated from a much larger predecessor (reported 1,428 → 179
  lines) — that consolidation's exact equivalence to the predecessor is
  **still unverified**, flagged honestly in the toolkit's own docs (see
  §6).
- **`llmos_toolkit/`** — a small, dependency-light Python CLI that
  checks whether those rules are actually being followed: drift
  detection, integrity pinning, secret scanning, retrieval, git-based
  sync. 13 plugins as of 2026-08-14, all tested against real files
  during development, not just written and assumed to work.

The name "Socrates LLMOS" is a nickname earned over the course of
building it, not a product or a rebrand of any code — `llmos_toolkit`
stays that name because renaming it breaks Python's import resolution
(confirmed the hard way once already).

## 2. Directory structure

```
llmos_project/
├── LICENSE                      MPL 2.0, in every major folder
├── pyproject.toml               pip-installable, no PYTHONPATH needed
├── kernel/                      hand-maintained behavioral spec (6 files)
├── llmos_toolkit/                the CLI package — see §3
├── docs/                        narrative docs — README, manuals, this file, CHANGELOG
├── state/                       audit/integrity artifacts — ledgers, pins, drift baselines
├── rag/                         retrieval artifacts — index db, generated handoff doc
├── projects/                    real work-product (depolarize prompt, threat-response ref)
└── reference/                   archived history, not actively maintained
```

## 3. The toolkit — all 13 plugins, current as of last test pass

| Command(s) | What it does | Tested how |
|---|---|---|
| `check`, `check-dir`, `log` | Line-count drift, refuses unjustified growth | Original standalone tool, migrated |
| `drift-check`, `drift-add-rule` | Surface-pattern drift rules (requirements.json-style) | Ran against real kernel text |
| `flag-claims` | Advisory scan for absolute language / unsourced claims | Caught a planted overclaim in testing |
| `token-audit`, `token-log` | Rough chars/4 token estimate + ledger | — |
| `drift-log`, `drift-log-signatures`, `drift-log-confirm` | 5-class adaptive drift check (growth/semantic/cross-artifact/embedded/structural), conservative self-adaptation | Two real bugs found and fixed during build; this session confirmed it correctly localizes a deliberately-planted single-word semantic drift |
| `sync-status` | Pointer to sync options | — |
| `git-sync-status/-pull/-push` | One-shot git-based multi-device sync — **no daemon, no live connection** | Real two-clone round trip: commit in one, pulled by the other |
| `rag-index`, `rag-query`, `rag-handoff` | Local TF-IDF keyword retrieval + handoff generation — **not semantic search**, stated explicitly | Indexed the real 41-file project, real queries returned correct files |
| `scan-secrets` | Regex + entropy scan for hardcoded credentials | Ran against all 109 project files; self-exclusion confirmed; URL and backtick-filename false positives fixed this session |
| `audit-all` | Chains secret scan + **real SHA-256** kernel verification | Full lifecycle tested: unpinned→fail, pinned→pass, tampered→caught with exact hash mismatch shown |
| `session-close` | Re-index → handoff regen → drift-log → commit → ledger compact, one call | Full pipeline tested end-to-end, including a forced compaction run on the real ledger |
| `ledger-compact` | Rolls old ledger entries into a permanent skeleton summary, keeps recent entries raw | Tested on a scratch copy before any real use; idempotence confirmed (skeleton never re-summarized) |
| Built-ins: `trust-plugin`, `scan-plugin`, `pin-kernel`, `verify-kernel`, `kernel-hook` | Plugin trust pinning, kernel integrity | `require_trust` mode tested: tampered plugin correctly refused before import, never executed |

Full detail on every command: `llmos_toolkit/README.md` (technical) and
`llmos_toolkit/HOW_TO_USE_THIS.md` (plain-language, no CLI experience assumed).

## 4. How to run it

```bash
cd llmos_project
pip install -e . --break-system-packages --no-build-isolation
llmos --list-commands
```

`--no-build-isolation` is required in network-restricted environments —
confirmed necessary in this project's own dev sandbox. Without pip
install, the fallback is `PYTHONPATH=/path/to/llmos_project` run from
inside `state/`.

## 5. Licensing

MPL 2.0 — full official text (fetched directly from mozilla.org, not
reconstructed from memory) in `LICENSE` at root and in every major
folder — that placement is explicitly sanctioned by the license's own
Exhibit A. 78 source/doc files carry the standard header notice.
`NOTICE.md` explains the project name.

## 6. Known open items — logged, not built

- **Kernel consolidation equivalence is SPOT-CHECKED (partial), not fully
  verified.** The exact 1,428-line file the original consolidation ran
  against (sha256_12 `0fd93baf5538`, per `growth_ledger.jsonl`'s first
  entry) has not been located and may be unrecoverable. A structurally-
  consistent 820-line snapshot from the same P3 lineage was supplied
  2026-08-14 and used to spot-check 4 of ~14 merged/compressed kernel
  sections against `SEMANTIC_DRIFT_POLICY.md`'s protocol — see the
  `semantic_spot_check` ledger entry for the full breakdown. Result: no
  decision-changing drift found in the 4 checked sections (2 minor,
  non-decision-changing phrasing losses noted); 2 sections initially
  suspected cut were confirmed correctly preserved as standalone files
  (`HCF_LLMOS_Compatibility_Adapter_v1_3.md`,
  `HCF_LLMOS_Precision_Refactor_Calibration_v1.md`) rather than lost.
  Remaining ~10 sections still unchecked. Kernel header updated to state
  this tier accurately.
- **RAG is keyword-based (TF-IDF), not semantic**, by deliberate choice —
  Chroma/LanceDB were considered and rejected for pulling in ML-
  framework weight, a bad fit for the stated Android/Termux portability
  goal. Revisit only if keyword search demonstrably isn't enough.
- **Sync is one-shot git only, no real-time option** — deliberately not
  built; would need an actual backend, different risk profile, logged
  as a real future option, not started.
- **`AI-Coordination-070526.zip`** is explicitly excluded from this
  project. Contains what looks like real credential material in
  `DO-NOT-SYNC/activepieces-secrets.md` — never opened beyond confirming
  its shape, never included in anything packaged.
- **Security hardening is on hold as of 2026-08-14** — put on hold
  deliberately, not abandoned. If a real at-risk-user (journalist/
  authoritarian-context) use case becomes near-term, this project stays
  household-only and a separate, cleanly-started repo (no inherited git
  history) is where hardened work happens — never a fork of this repo's
  history. One specific item flagged for that future work, so it isn't
  lost in the meantime: **`WELLBEING_FLAG_HANDLING_ADDENDUM.md` as
  written assumes it's safe to plainly name what was noticed. In a
  hardened context, even a locally-stored record of "flagged distress"
  is dangerous if the device is compromised, regardless of intent — a
  hardened variant would need to persist only that review happened, not
  what was flagged.** The main kernel's reasoning methodology is
  probably fine unchanged, since it isn't user data — that assessment
  itself is unverified pending a real threat model, same as everything
  else in this note.

## 7. What's out of scope for this handoff

A separate, extended discussion in this conversation involved an
"HCF/LLMOS" framework audit request and a proposed multi-instance
consensus/escalation mechanism. That request was declined, repeatedly,
across the conversation — it is **not part of this project** and isn't
reflected in anything above. If picking this project back up elsewhere,
that thread doesn't need to come with it.

## 6a. Session log — 2026-08-14

- **Real bug fixed:** `pin-kernel` wrote to a hardcoded relative path
  (`Path("kernel_pins.json")`, resolved against CWD) instead of
  `state/kernel_pins.json` via the project's own `paths.get_state_path()`
  helper — meaning `audit-all` could never find a pin `pin-kernel` had
  just written. Fixed in `llmos_toolkit/core/cli.py`; verified end-to-end
  (pin → audit-all now passes).
- **Real bug fixed:** `scan-secrets`' entropy check flagged long URL path/
  query segments (e.g. a wandb.ai report link) as high-entropy tokens —
  false positives, since URLs are unlikely to be a hardcoded credential
  in that shape. Fixed in `secret_scanner/plugin.py` to exclude tokens
  falling inside a `https?://` span on the same line; confirmed real
  secret patterns (API keys, entropy on non-URL tokens) still fire
  correctly.
- `drift-log`, `flag-claims`, `rag-index`/`rag-query` all run and behave
  as documented (40 files indexed, matches this doc's own count).
- Kernel equivalence: see updated §6 above.
- Full `audit-all` passes clean as of this session (100 files scanned,
  kernel pin verified against current hash `3cf252ee8bf4…`).

## 6b. Session log — 2026-08-14 (continued): wellbeing-flag handling

New standalone file: `kernel/WELLBEING_FLAG_HANDLING_ADDENDUM.md`.
Written after a real incident, not hypothetically: an instance treated
an imprecise hour-count remark as a diagnosis, escalated unilaterally
(crisis-line referral), then wouldn't accept a later correction to that
figure and locked the session, refusing further work. The addendum is
deliberately kept separate from the artifact-delta loop-detection gate
(`state_anchored_interrupt_policy.md`, uploaded separately, not yet
added to this project) — a wellbeing flag and a stalled-work loop are
different failure modes and must not share a lockout mechanism.
Six rules: name once without displacing the task, offer resources only
for genuine crisis signals, don't diagnose from ambiguous data, never
lock the session or require the flag "resolved" to continue, don't
auto-escalate on thin evidence, and treat a stated correction as new
evidence to incorporate — not something to be argued down.

**Done (was open, closed 2026-08-14):** the artifact-delta loop-detection
policy is now `kernel/ARTIFACT_DELTA_LOOP_DETECTION_POLICY.md`, adapted
from the uploaded `state_anchored_interrupt_policy.md` / the
Gemini-Claude revision cycle in `policy_revision_report.md`, symbol
shorthand removed per the same cross-model trust audit applied to the
other kernel files.


The toolkit is in a stable, tested state — nothing pending or half-built.
Reasonable next steps, in rough order of how contained they are:
1. If the exact 1,428-line predecessor ever turns up, complete the
   remaining ~10-section spot-check (or go for full VERIFIED-EQUIVALENT)
   using `SEMANTIC_DRIFT_POLICY.md`'s protocol — §6 has the current
   partial result to build on.
2. Decide whether the `depolarize` and `threat_response` projects need
   further work, independent of the toolkit itself.
3. Only if a concrete need shows up: real-time sync, semantic RAG, or
   anything else currently logged as open.

Nothing here is urgent. The project's actual state is: built, tested,
documented, licensed, and safe to leave alone until there's a real
reason to pick it back up.
