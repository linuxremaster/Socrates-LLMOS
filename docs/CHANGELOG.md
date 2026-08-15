<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Changelog

Dated entries, most recent first. For full commit-level detail see
`git log`; this file is the human-readable summary. For per-file
provenance see `state/growth_ledger.jsonl`.

Versioning: [SemVer](https://semver.org/) for git tags and releases
(`v0.1.0-alpha`), [PEP 440](https://peps.python.org/pep-0440/) for the
Python package version in `pyproject.toml` (`0.1.0a0`) — the two
formats differ by convention, not by version. Pre-1.0: expect breaking
changes between minor versions.

## v0.1.0-alpha — 2026-08-14

First versioned snapshot. Project renamed from `llmos_project` to
`socrates_llmos` (folder name only — no content change, git history
preserved via plain directory rename). Everything below this line was
built before formal versioning started; this tag marks the point
versioning began, not a feature cutoff.

## 2026-08-14

**Bug fixes (systemic — same class across the whole toolkit):**
- Found and fixed 7 instances of a hardcoded relative-path bug: file
  constants like `Path("kernel_pins.json")` resolved against whatever
  directory a command happened to be invoked from, instead of a fixed
  project location. Affected `pin-kernel`, `handoff_rag`,
  `adaptive_drift_logger` (2 files), `growth_budget`, `token_audit`,
  `drift_check`. All now route through `paths.get_state_path()` or the
  new `paths.get_rag_path()`.
- `scan-secrets` false-positived on long URLs and markdown-backtick
  filenames (read as high-entropy tokens). Fixed by excluding both span
  types from the entropy check only — named-pattern checks (API keys
  etc.) still fire correctly inside either.

**New kernel policy files:**
- `WELLBEING_FLAG_HANDLING_ADDENDUM.md` — written after a real
  incident: an instance treated an imprecise remark as a diagnosis,
  escalated unilaterally, then wouldn't accept a correction and locked
  the session.
- `ARTIFACT_DELTA_LOOP_DETECTION_POLICY.md` — adapted from a
  user-supplied 5-pass Gemini/Claude revision cycle; detects a stalled
  work loop from artifact delta (file/claim/evidence-tier change), not
  text variance.

**Cross-model trust audit:**
- Removed all arrow-chain and inequality-symbol shorthand from
  `HCF_LLMOS_Kernel_v1.3.6-C.md`, `SEMANTIC_DRIFT_POLICY.md`, and
  `UNIFIED_BEHAVIORAL_OUTPUT_PROTOCOL_v2.md` — flagged as
  pattern-matching to command/runtime syntax by at least one host model
  regardless of surrounding disclaimer prose. Every rule now states in
  plain sentences as its sole operative form. Confirmed via
  `drift-log`/`drift-log-confirm` on all 17 flagged sections — no
  decision-changing meaning loss found.

**Kernel equivalence spot-check:**
- Compared 4 of ~14 merged/compressed sections against a
  structurally-verified P3 predecessor snapshot (not sha256-matched to
  the exact 1,428-line file the original consolidation used). No
  decision-changing drift found; 2 sections initially suspected cut
  were confirmed correctly preserved as standalone reference files.

**New tooling:**
- `session-close` — one command: re-index, regenerate
  `rag/SESSION_HANDOFF.md`, drift-log all kernel files, commit, compact
  ledgers. Closes the staleness gap where retrieval/drift state only
  updated when someone remembered to run it manually.
- `ledger-compact` — rolls old jsonl ledger entries into a permanent
  skeleton summary, keeps recent entries in full. Runs automatically as
  `session-close` step 5 (default keep: 20), or standalone.

**Reorganization:**
- New `docs/` folder — README, MANUAL_START_HERE, NOTICE,
  PROJECT_HANDOFF_SUMMARY, INSTANCE_ORIENTATION_SEQUENCE, this file.
- New `rag/` folder — retrieval artifacts (`handoff_rag.db`,
  `SESSION_HANDOFF.md`), separated from `state/` (audit/integrity
  artifacts only) so a RAG rebuild never touches audit history.

**New documentation:**
- `docs/INSTANCE_ORIENTATION_SEQUENCE.md` — 8-step order for a new
  model instance adopting this project: safety/adoption boundary first
  (steps 1–7), project substance second (step 8).

**Docs refreshed to match current state:** `docs/README.md`,
`docs/MANUAL_START_HERE.md`, `llmos_toolkit/README.md`,
`llmos_toolkit/HOW_TO_USE_THIS.md`, `docs/PROJECT_HANDOFF_SUMMARY.md` —
directory structure, plugin count (11 → 13), install instructions (no
longer requires `cd state` + manual `PYTHONPATH`), new command
reference entries.

**End Changelog**
