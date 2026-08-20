<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# LLMOS Toolkit — Modular Plugin CLI

*Originally conceived as a conflict resolution management system; became this epistemic-discipline kernel and toolkit for LLM work through a real redirection -- see `docs/PROJECT_PRIORITIES.md`'s Origin and Scope Evolution section.*

A dynamic-discovery, plugin-based command-line toolkit. Requires Python 3.11+
(uses stdlib `tomllib`). Run from the directory that *contains* this
`llmos_toolkit/` folder:

```
python -m llmos_toolkit --list-commands
```

## Architecture

```
llmos_toolkit/
  __main__.py          entrypoint for `python -m llmos_toolkit`
  config.toml           plugin_dirs, enabled/disabled, trust settings
  adaptive_drift_logger.py   standalone 5-class drift tool, canonical copy
  core/
    registry.py          the registration API — plugins register commands here
    plugin_loader.py      scans plugin_dirs, dynamically imports, runs security checks
    config.py             loads config.toml into a ToolkitConfig
    security.py           hashing, permission checks, advisory static scan
    cli.py                argparse wiring, built-in commands (incl. kernel-hook), dispatch
  plugins/
    growth_budget/plugin.py         example: explicit register(registry) style
    example_hello/plugin.py         example: @registry.command(...) decorator style
    drift_check/plugin.py           surface-drift checker (requirements.json-style rules)
    claim_flag/plugin.py            advisory scan for absolute language / unsourced claims
    token_audit/plugin.py           rough token/cost estimation and logging
    adaptive_drift_logger/plugin.py thin wrapper exposing adaptive_drift_logger.py as commands
    sync/plugin.py                  pointer to git_sync + general sync guidance
    handoff_rag/plugin.py           local TF-IDF retrieval + handoff doc generation, no API/network
    git_sync/plugin.py              git pull/push/status - one-shot only, no daemon/watcher/live connection
    secret_scanner/plugin.py        regex + entropy scan for hardcoded credentials
    audit_all/plugin.py             secret scan + real cryptographic kernel verification, one pass
    session_close/plugin.py         re-index, handoff regen, drift-log, commit, compact -- one call, best-effort not transactional
    ledger_compact/plugin.py        rolls old ledger entries into a permanent skeleton, keeps recent entries raw
    paste_handoff/plugin.py         real, current handoff summary for a fresh instance or a paste-into-Gemini-style handoff
    policy_diff/plugin.py           save/diff policy-text snapshots over time, path-traversal-safe naming
    behavior_log/plugin.py          the observation/adoption/quirk/experiment tracking system -- log-observation, clause-adoption-report, propose-observation/approve-pending (real quarantine boundary for unverified instance claims), experiment-report, quirk-report
    sandbox_runner/plugin.py        real CPU/memory-limited, credential-stripped subprocess execution for experimental code -- NOT container isolation, see docs/SANDBOX_RUNNER_GUIDE.md
  hooks/
    pre-commit            git pre-commit template, NOT auto-installed — see Hooks below
```

## Installing without PYTHONPATH

The toolkit can also be installed as a normal Python package instead of
using the `PYTHONPATH` approach shown elsewhere in this file:

```
cd socrates_llmos
pip install -e . --break-system-packages --no-build-isolation
```

`--no-build-isolation` is required in network-restricted environments —
pip's isolated build step otherwise tries to fetch `setuptools` even
when it's already installed; confirmed necessary and sufficient during
this project's own development. After install, `llmos --list-commands`
works from any directory, no `PYTHONPATH` needed. Adds `numpy` as a
declared dependency (already required by `handoff_rag`) — nothing else.

**How discovery works:** on every run, `plugin_loader.discover_plugins()`
scans each directory in `config.toml`'s `plugin_dirs` for either a
subdirectory containing `plugin.py`, or a top-level `*_plugin.py` file.
Each is dynamically imported via `importlib.util`. A plugin registers its
commands either with the `@registry.command(...)` decorator at import
time, or by defining `def register(registry): ...`, called right after
import. New commands appear in `--list-commands` and become runnable
immediately — no other file needs to change to add a plugin.

**Writing a new plugin:** copy `plugins/example_hello/` as a template for
a single command, or `plugins/growth_budget/` for several related ones.
Drop it under `plugins/`, and it's picked up on the next run.

## Commands reference

Beyond the built-ins (`trust-plugin`, `scan-plugin`, `pin-kernel`,
`verify-kernel`, `kernel-hook` — see Security and Hooks below):

| Command | Plugin | What it does |
|---|---|---|
| `check`, `check-dir`, `log` | growth_budget | Line-count drift, unjustified-growth refusal |
| `hello` | example_hello | Decorator-style registration demo |
| `drift-check`, `drift-add-rule` | drift_check | Surface-level drift rules (same pattern as the depolarize toolkit's requirements.json) — starts empty, catches only what you've explicitly added |
| `flag-claims` | claim_flag | Advisory scan for absolute language and unsourced factual-shaped claims — pattern match, not verification |
| `token-audit`, `token-log` | token_audit | Rough token/cost estimate (chars/4) and ledger, comparable across sessions, not exact per-provider |
| `drift-log`, `drift-log-signatures`, `drift-log-confirm` | adaptive_drift_logger | Five-class adaptive drift check (growth/semantic/cross-artifact/embedded/structural), baseline-based, conservative self-adaptation — see `adaptive_drift_logger.py`'s own docstring for full detail |
| `sync-status` | sync | Reports the sync slot is empty/unconfigured — see Sync below |
| `rag-index`, `rag-query`, `rag-handoff` | handoff_rag | Local retrieval over indexed markdown (SQLite + pure-NumPy TF-IDF, no API/network) and pointer-based handoff doc generation. **Keyword/TF-IDF overlap, not semantic search** — finds shared vocabulary, not shared meaning. |
| `git-sync-status`, `git-sync-pull`, `git-sync-push` | git_sync | Multi-instance/multi-device coordination via plain git. **One-shot commands only — no daemon, no webhook, no live connection.** Tested with a real two-clone round trip during development. |
| `scan-secrets` | secret_scanner | Regex + Shannon-entropy scan for hardcoded credentials. Advisory, same as `security.py`'s scan. Excludes its own plugin directory from every check — a scanner named "secret" would otherwise flag itself on its own filename every run. |
| `audit-all` | audit_all | Runs `scan-secrets` + a **real** SHA-256 kernel-pin check in one pass. Fails clearly if the kernel is unpinned or tampered — no stub, no fake PASS. |
| `session-close` | session_close | Re-index → regenerate `rag/SESSION_HANDOFF.md` → drift-log all kernel files → commit → compact ledgers, in one call. Run at the end of a working session so retrieval and drift baselines never go stale from someone forgetting a manual step. `--no-commit`, `--no-compact`, `--compact-keep N`, `--message` available. |
| `ledger-compact` | ledger_compact | Rolls old raw entries in a jsonl ledger into one permanent skeleton summary (event counts, date range, files touched), keeps the N most recent raw entries in full (`--keep`, default 20). Idempotent — an existing skeleton is never re-summarized. Runs automatically as `session-close` step 5, or standalone on any ledger file. |
| `paste-handoff` | paste_handoff | Real, current project state as one paste-ready block (recent commits, open items) — for a fresh instance picking up context, or handing off to another provider. |
| `save-policy-snapshot`, `diff-policy-snapshot` | policy_diff | Save/diff snapshots of policy text over time. Microsecond-precision timestamps (same-day saves stay distinct), snapshot names sanitized against path traversal. |
| `log-observation`, `record-outcome`, `behavior-summary` | behavior_log | Core observation logging — subject, category, severity, verified-or-asserted, plus outcome tracking after cross-examination. |
| `kernel-adoption-summary`, `log-clause-adoption`, `clause-adoption-report` | behavior_log | Which kernel principles have logged evidence of real use; per-clause adopt/decline positions across instances, most-contested first. |
| `propose-observation`, `review-pending`, `approve-pending`, `reject-pending` | behavior_log | The real quarantine boundary: a free-tier/sandboxed instance can stage an observation, but only an explicit human command commits it to the real ledger. |
| `experiment-report`, `quirk-report` | behavior_log | `--experiment-id` groups a bounded, manually-supervised session's entries into one reviewable arc. `--quirk-id` groups recurring behavioral patterns across subjects, modeled on Anthropic's real AuditBench "quirks directory" design. |
| `sandbox-run`, `sandbox-list`, `sandbox-reset` | sandbox_runner | Real CPU/memory limits, disposable directory, stripped credentials for running experimental code. **Not container isolation** — see `docs/SANDBOX_RUNNER_GUIDE.md` for exact scope. |
| `log-boundary-update` | adaptive_drift_logger | Records a checked provider/regulatory-policy change (provider, summary, `--source`, `--verified`) — feeds `EXECUTION_BOUNDARY_UPDATES.md`. |
| `self-test` | self_test | Runs the project's own real `unittest` suite (`--verbose` for per-test names/docstrings) — this is what `llmos self-test` actually calls. |
| `version-drift-summary` | adaptive_drift_logger | Cross-model-version comparison summary over logged drift signatures. |

## Hooks

`hooks/pre-commit` is a template, **not installed automatically**. To
activate it in a git repo:
```
cp llmos_toolkit/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
It runs `kernel-hook` (integrity + adaptive drift, combined) before each
commit and blocks the commit on failure. What actually triggers it is
git itself, on `git commit` — an ordinary shell script, same as any
other pre-commit hook. Nothing about the kernel document or any AI model
causes this to run on its own. Edit `KERNEL_FILES` in the script to the
files you want checked. The script assumes `llmos_toolkit/` sits inside
your git repo root (so `PYTHONPATH=$REPO_ROOT` resolves the package) —
if your repo root *is* the toolkit itself, adjust that line.

## Sync

`git_sync` is a real, tested implementation: plain `git` commands
(status/pull/push), each one-shot — run when you invoke it, does one
thing, exits. **Not a live or persistent connection.** No daemon, no
webhook, no reaction to remote events — matches Claude's own actual
product limits around GitHub (conversation-only, no event triggers) and
this project's existing multi-instance model (async pull/push through
shared storage, human or session as transport). Round-trip tested
during development: a change committed in one clone was correctly
pulled into a separate clone, simulating two coordinating instances.

`sync-status` remains the general pointer for anything git_sync doesn't
cover — putting state files in any synced directory (Syncthing,
Dropbox, etc.) needs no toolkit code at all.

## State files

Several commands create a local file on first use. None are pre-created
by the package; all are plain JSON/JSONL, safe to inspect or delete:

| File | Created by | Contents |
|---|---|---|
| `growth_ledger.jsonl` | `check`, `check-dir` | Line-count diff history |
| `token_ledger.jsonl` | `token-audit` | Token/cost estimate history |
| `drift_rules.json` | `drift-add-rule` | Tracked surface-drift rules |
| `kernel_pins.json` | `pin-kernel`, `kernel-hook` | Kernel file integrity baselines |
| `.drift_state.json` | `drift-log` | Adaptive drift logger baselines + learned signatures |
| `drift_audit.jsonl` | `drift-log` | Append-only history of every drift-log run — periodically compacted by `ledger-compact`/`session-close`, older entries roll into a permanent skeleton summary rather than growing forever |
| `rag/handoff_rag.db` | `rag-index` | TF-IDF retrieval index — separate `rag/` folder, not `state/`, so a full RAG rebuild never touches audit history |
| `rag/SESSION_HANDOFF.md` | `rag-handoff`, `session-close` | Generated pointer doc for a fresh instance to read first |

## Security

**Software boundary:** this package is an ordinary Python CLI/plugin toolkit. It executes code when invoked by the user or by normal operating-system mechanisms such as Git hooks. It is not an autonomous LLM agent, persistent model runtime, or background orchestration service. See `docs/LLMOS_SCOPE_AND_BOUNDARIES.md` for the full kernel-vs-toolkit distinction.

Dynamic import means importing a plugin file executes its top-level code
— every Python plugin system works this way (pytest, Sphinx, Flask
extensions included). This toolkit adds real controls around that fact,
and is explicit about what is and isn't a security boundary.

**The actual boundary — trust pinning.** Set `require_trust = true` in
`config.toml` and list each plugin's expected sha256 under `[trust]`. A
plugin only imports if its file's current hash matches exactly. An
unpinned or tampered plugin is refused *before* it's ever imported — its
code never runs. Compute a pin with:

```
python -m llmos_toolkit trust-plugin <name> plugins/<name>/plugin.py
```

Paste the printed line under `[trust]` in `config.toml`. If a trusted
plugin file changes afterward (edited, tampered, or just updated by
you), it's refused on the next run until re-pinned — this is intentional
even for your own edits; re-run `trust-plugin` after a legitimate change.

**Advisory only — not a boundary.** Independent of trust mode, every
discovered plugin is checked for group/world-writable permissions (a
real local-privilege-escalation path on a shared machine) and scanned
with a small regex set for `subprocess`, `os.system`, `eval`, `exec`,
`__import__`, and common network imports. Findings are printed with
`--list-commands --verbose`, or standalone via `scan-plugin <path>`.
This scan is trivially bypassed (string-building, `getattr` indirection,
base64, etc.) — treat a clean result as "nothing obvious," never as
"safe." Nothing here sandboxes plugin code; a trusted, pattern-clean
plugin still runs with full process privileges.

**Kernel integrity pinning.** Separately, `pin-kernel <file>` and
`verify-kernel <file>` apply the same sha256 approach to a kernel/policy
markdown file — record a trusted baseline, then detect drift or
tampering later. Pins are stored in `kernel_pins.json` (created on first
use). This is a different concern from `growth_budget.py`'s line-count
check or `SEMANTIC_DRIFT_POLICY.md`'s meaning-equivalence tiers — this
one only asks "is this byte-for-byte what I last approved."

**Built-in commands are not plugins.** `trust-plugin`, `scan-plugin`,
`pin-kernel`, `verify-kernel`, and `kernel-hook` are wired directly into
the CLI core, not loaded through the plugin mechanism — they manage the
trust gate (or, for `kernel-hook`, combine two things that do), so they
must work even when `require_trust` blocks every plugin. Their names are
reserved; a plugin cannot register a command using any of them (enforced
in `registry.py`, checked at registration time — see
`RESERVED_COMMAND_NAMES`).

## Config reference (`config.toml`)

```toml
plugin_dirs = ["plugins"]     # dirs to scan, relative to this file or absolute
enabled = ["growth_budget"]   # optional allow-list; omit to allow all discovered
disabled = []                 # always-skip list; wins over `enabled`
require_trust = false         # true = enforce [trust] hash pins
[trust]
growth_budget = "…sha256…"
```

## Backward compatibility

The `growth_budget` plugin is a line-for-line migration of the original
standalone `growth_budget.py` script (same ledger format, same pass/fail
logic) — the original script and this plugin can read each other's
`growth_ledger.jsonl` interchangeably. Only the entry point changed.
