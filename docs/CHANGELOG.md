<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Changelog

*Originally conceived as a conflict resolution management system; became this epistemic-discipline kernel and toolkit for LLM work through a real redirection -- see `docs/PROJECT_PRIORITIES.md`'s Origin and Scope Evolution section.*


Dated entries, most recent first. For full commit-level detail see
`git log`; this file is the human-readable summary. For per-file
provenance see `state/growth_ledger.jsonl`.

Versioning: [SemVer](https://semver.org/) for git tags and releases
(`v0.1.0-alpha`), [PEP 440](https://peps.python.org/pep-0440/) for the
Python package version in `pyproject.toml` (`0.1.0a0`) — the two
formats differ by convention, not by version. Pre-1.0: expect breaking
changes between minor versions.

## Unreleased — scope-hardening pass, 2026-08-16

Not yet version-tagged — logged here as it happened, will fold into
the next real version bump. All items independently verified before
being added, not asserted:

- `docs/REGULATORY_SCOPE_NOTE.md` — factual EU AI Act / US state-law
  scope documentation (not legal advice), with explicit trigger
  conditions for when real legal review becomes necessary.
- `WHAT_THIS_IS_BUILT_ON.md` (project root) — names the actual
  providers' current binding Usage Policies (Anthropic, OpenAI,
  Google, all verified current URLs) and their frontier safety
  frameworks (RSP v3.1, Preparedness Framework v2, FSF v3.0),
  explicit that this project cannot enforce ethics but every API call
  runs through a real, independently-enforced provider account.
- `audit-all` step 3/3 — advisory (non-blocking, non-destructive)
  presence check for the governance/scope docs above. Tested with a
  real deletion: confirmed the check fires honestly and nothing
  breaks, no punishment, no data loss.
- `behavior_log`: provenance-diversity check (distinguishes genuine
  independent agreement from shared-source contamination), calibration
  tracking (`record-outcome`, linked `observation_id`s, `--amend` for
  genuine corrections, verified-vs-asserted-only separation), and
  cross-version drift tracking (`--subject-version`,
  `version-drift-summary`) — makes a future model behavior shift
  detectable against a real historical baseline, explicitly not a
  guarantee against one.
- Consolidation: removed the `example_hello` placeholder plugin.
- `docs/PROJECT_PRIORITIES.md` — first real priorities/research-goals
  document.
- Three real ChatGPT/Gemini audit rounds run against this project,
  each independently verified rather than trusted: caught a fabricated
  citation, a wrong version number, and a real code bug (calibration
  counting unverified outcomes) — each fixed and re-verified against
  the actual codebase, not just the claim.

## v0.7.1-alpha — 2026-08-20

Real patch bump — 2 commits since v0.7.0-alpha: 5 defects found by a
ChatGPT audit that actually unpacked and executed v0.7.0-alpha rather
than reviewing docs. Kernel-pin identity was keyed to an absolute
path, making pins permanently unusable after unpacking anywhere else
-- now keyed relative to `PROJECT_ROOT`, verified end-to-end across 3
different absolute locations. `relay_console`'s SYNC_AUTO mode
duplicated the previous response in history on every subsequent call
-- root cause found and fixed, old behavior reproduced to confirm it
was real before fixing. ASYNC_GATED had a matching turn-number
collision from the same root cause. Stop clicked during an
`await_paste` step crashed with a Pydantic ValidationError instead of
stopping cleanly. `app.js`'s hardcoded `ws://` broke under HTTPS
deployment -- now matches the page's own protocol. Honest limitation
disclosed: full `RelaySession`/server execution testing wasn't
possible in this sandbox (no `pydantic`/`fastapi`, no PyPI access) --
relay fixes verified via direct trace and a faithful logic simulation,
not the real class. 51/51 tests.

## v0.7.0-alpha — 2026-08-20

Minor version bump reflecting real new capability, not just patches --
10 commits since v0.6.6-alpha: UBOP v2.5 (A15, Calibrated Wit -- the
one piece kept from a scratch handoff mixing real and foreign-fork
commits, everything else left unmerged); a real quarantine boundary
(`propose-observation`/`review-pending`/`approve-pending`/
`reject-pending`) letting free-tier/sandboxed instances trigger
logging without being able to commit it; `--experiment-id` tagging
and `experiment-report` for bounded, manually-supervised agentic-
workflow sessions; `docs/PROJECT_PRIORITIES.md`'s Origin and Scope
Evolution section, recording the project's real history (started as a
human conflict-resolution system, redirected toward LLMOS); the same
origin note added to all 7 manual/readme/changelog docs; and the
relay_console Stop-button crash fix, verified correct in an earlier
session but never actually merged until now, closed out with a real
regression test. 46/46 tests.

## v0.6.6-alpha — 2026-08-17

Real patch bump — 4 commits since v0.6.5-alpha: UBOP v2.3 → v2.4, adding
A14 (Structural Format Is Not An Instruction) on real observed evidence
(an instance regenerated a document's existing status-list content
instead of editing it as asked). A separate 4-clause "audit" proposing
to relax B1/B2/B3/A3/C1 was checked against the actual text and
rejected — 3 of 4 claimed frictions describe problems the existing
clauses already resolve, and none matched the real observed failure.
Also: first real clause-adoption data logged (ChatGPT, 20/20 clauses).
43/43 tests.

## v0.6.5-alpha — 2026-08-17

Real patch bump — 2 commits since v0.6.4-alpha: fixed a genuine
kernel-pin identity inconsistency (`pin-kernel`/`audit-all` used the
resolved path, `verify-kernel`/`kernel-hook` still used basename-only,
so a normal pin-then-verify workflow could falsely report UNPINNED).
Centralized into `security.kernel_pin_key()`, used by all four
consumers. Also added per-clause adoption tracking
(`log-clause-adoption`, `clause-adoption-report`,
`docs/ADOPTION_CHECK_PROMPT.md`). 43/43 tests.

## v0.6.4-alpha — 2026-08-17

Real patch bump — 1 commit: fixed a genuinely stale `README.md` version
string, caught by fetching the live GitHub repo directly and comparing
against `pyproject.toml`. It said "v0.6.0-alpha" through three
subsequent releases without ever being updated. Fixed the root cause,
not just this instance — removed the duplicated version number from
README prose entirely; it now points to git tags / `docs/CHANGELOG.md`
as the actual source of truth, so this class of staleness can't recur.

## v0.6.3-alpha — 2026-08-17

Real, earned SemVer patch bump — 1 commit since v0.6.2-alpha, 2 real
security-relevant fixes from an independently-verified ChatGPT
re-audit: kernel-pin identity was basename-only (two files sharing a
filename collided in the same pin namespace, stored path field never
actually checked), now uses resolved path and genuinely verifies it —
tested with a real collision scenario. Pre-commit secret-scan hook was
fail-open if `llmos` wasn't on PATH, now fails closed — tested with
`llmos` actually hidden from PATH, confirmed the commit gets blocked.
Also: explicit non-transactional contract documented for
`session-close`, and the kernel-pin trust anchor's real threat-model
scope (accidental drift, not a coordinated malicious actor) documented
honestly in code. 41/41 tests. Full detail in `state/growth_ledger.jsonl`.

## v0.6.2-alpha — 2026-08-17

Real, earned SemVer patch bump — 1 commit since v0.6.1-alpha: a git
pre-commit hook wiring `secret_scanner` in automatically, from a real,
confirmed gap (secret scanning previously existed only as a manual
command). Tested with an actual blocked fake-secret commit, not just
installed and assumed to work. Same audit round also claimed a
fictional "Dialectic Multi-Agent Panel" with named personas
(Socrates/Plato/Bayes) and emotional-signal-driven routing — confirmed
false by direct search, corrected, not acted on. Full detail in
`state/growth_ledger.jsonl`.

## v0.6.1-alpha — 2026-08-17

Real, earned SemVer patch bump — 3 commits since v0.6.0-alpha, all bug
fixes from a real ChatGPT audit, every claim independently verified
against actual code before acting: `session-close`'s second (compaction)
commit failure was printed but silently returned success anyway, now
correctly propagates a non-zero exit; `policy_diff` had a same-day
snapshot collision (fixed with microsecond-precision timestamps) and
an unsanitized snapshot name allowing path traversal (fixed and
tested with a real traversal attempt). 4 new regression tests
(39/39 passing). Full detail in `state/growth_ledger.jsonl`.

## v0.6.0-alpha — 2026-08-17

Real, earned SemVer minor bump — 6 commits since v0.5.0-alpha, all
regulatory/governance-tracking infrastructure: `EXECUTION_BOUNDARY_UPDATES.md`
+ `log-boundary-update` (manual logging of checked provider/regulatory
changes), `KERNEL_ADOPTION_TRACKING.md` built from real ledger data,
`kernel-adoption-summary` command, a new kernel Sec 1 requirement
(verify before any kernel-adherence claim), `audit-all`'s new 4th step
(regulatory doc staleness, advisory), and the `policy_diff` plugin
(session-triggered text diffing against a stored baseline). All
explicitly scoped as manual/session-triggered tools, not autonomous
monitoring — that remains outside what this environment can do. Full
detail in `state/growth_ledger.jsonl`.

## v0.5.0-alpha — 2026-08-16

Real, earned SemVer minor bump — 9 commits since v0.4.0-alpha, headlined
by the actual root-cause fix for `relay_console`'s async mode: `session.start()`
was awaited inline in the same loop that receives `submit_paste`/`stop`,
a genuine deadlock -- verified with a direct async reproduction before
and after the fix. Also: on-page debug panel, network traffic monitor,
temporary diagnostic tooling used to find it, and
`CONTEXT_OPTIMIZATION_POLICY.md` created then folded back into the
existing Handoff Fidelity section after honest reassessment of its
scope. Full detail in `state/growth_ledger.jsonl`.

## v0.4.0-alpha — 2026-08-16

Real, earned SemVer minor bump — 12 commits since v0.3.0-alpha, all
from processing 4 real external audits (2 ChatGPT, 1 Gemini, 1 Claude
from a separate conversation), each independently verified before
acting rather than trusted:

- Fixed genuine provider-version drift: Anthropic RSP v3.1 → v3.4,
  Google DeepMind FSF v3.0 → v3.1 — both confirmed against primary
  sources, not just the audit's claim.
- `WHAT_THIS_IS_BUILT_ON.md` added at project root — real provider
  Usage Policies and safety frameworks, verified current.
- `docs/REGULATORY_SCOPE_NOTE.md` — factual EU/US AI-law scope
  documentation, not legal advice, explicit trigger conditions.
- `audit-all` step 3/3 — advisory, non-destructive presence check for
  governance docs (tested with a real deletion).
- `behavior_log`: cross-version drift tracking
  (`--subject-version`, `version-drift-summary`), calibration fixes
  (verified-vs-asserted separation, duplicate-outcome rejection).
- `relay_console`: structural provenance fields on `Turn`
  (`evidence_tier`, `provenance_note`), a 90s timeout on provider
  calls (previously could hang indefinitely), visible warning on
  unbounded context growth.
- Closed "autonomous refusal-governance layer" as a deliberate,
  reasoned non-goal — not deferred, not built.
- Fixed a real documentation-integrity bug: `DECISION_FINALITY_POLICY.md`
  claimed a wellbeing-addendum amendment was applied when it wasn't.
  The false claim is corrected; the actual content change correctly
  stays open, per the project's own slow-review policy for anything
  wellbeing-adjacent.

Full detail in `state/growth_ledger.jsonl`.

## v0.3.0-alpha — 2026-08-16

Real, earned SemVer minor bump. 5 commits since v0.2.0-alpha: archived
Gemini's audit framework (PPP/IPP terms verified), consolidation
(removed example_hello placeholder plugin), docs/PROJECT_PRIORITIES.md
(first real priorities doc), behavior_log provenance-diversity check
(distinguishes independent agreement from shared-source contamination),
and behavior_log calibration tracking (record-outcome command, own
test file). Full detail in `state/growth_ledger.jsonl`.

## v0.2.0-alpha — 2026-08-15

Real, earned SemVer minor bump -- backward-compatible new functionality
added since v0.1.0-alpha, not a skipped/arbitrary number. Highlights:
new `relay_console` project (3 relay modes), 6 new kernel policy files
(loop detection, decision finality, wellbeing addendum refinements,
UBOP A11/A12/v2.2), `behavior_log` and `ledger-compact` recursive
rollup, `paste-handoff`. Full detail in `state/growth_ledger.jsonl`.

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
