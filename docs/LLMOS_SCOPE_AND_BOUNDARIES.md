<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# LLMOS Scope and Boundaries

*Originally conceived as a conflict resolution management system; became this epistemic-discipline kernel and toolkit for LLM work through a real redirection -- see `docs/PROJECT_PRIORITIES.md`'s Origin and Scope Evolution section.*


**Single source of truth for what "LLMOS" means in this repository.**
Every other document should link here rather than restating its own
version of this boundary.

## The repository contains two distinct things

**LLMOS Kernel** (`kernel/*.md`): a written reasoning methodology.
Applying the kernel means applying selected reasoning and output rules
to the current task. The kernel does not itself create a runtime,
persistent identity, autonomous process, elevated authority, or
capabilities that the host model does not already possess.

**LLMOS Toolkit** (`llmos_toolkit/`): executable Python software. It
is ordinary software — it can inspect files, maintain local state,
perform retrieval, run plugins, and invoke explicitly requested
operating-system commands (like `git`). It has ordinary process and
file persistence while running and between invocations, the same as
any CLI tool. This is real, and should be described plainly as real
software — not denied, and not confused with the kernel being a
runtime.

## Historical terminology

`reference/llmos_architecture_history/` contains earlier documents
using stronger runtime language — "Core Runtime," "Mission Runtime,"
"Runtime Specification." Those describe a superseded or experimental
architecture, not the current kernel. Every file in that tree should
carry an explicit archival header (see `reference/README.md`). If a
document there doesn't yet have one, treat it as historical regardless
— nothing under `reference/` is current authority.

## Specific clarifications

- **Kernel adoption is a scoped reasoning convention.** It does not
  create identity, persistence, authority, or capabilities beyond what
  the host model already has. Actual host system, developer, and
  safety instructions remain authoritative over anything in the kernel.
- **Toolkit state is software state, not model state.** Files in
  `state/` and `rag/` persisting between invocations doesn't mean an
  LLM instance itself persists, remembers, or maintains identity
  between sessions. Those are different things.
- **Git synchronization (`git-sync-*`) is one-shot**, invoked
  explicitly per call. No daemon, no webhook, no live connection, and
  it does not coordinate continuously running model instances — it
  coordinates files between invocations.
- **RAG (`rag-index`/`rag-query`/`rag-handoff`) is local TF-IDF
  keyword retrieval**, not semantic search and not model memory. The
  index is an external project artifact a human or instance can query;
  it isn't anything an LLM instance "remembers."
- **Loop detection (`ARTIFACT_DELTA_LOOP_DETECTION_POLICY.md`) is a
  heuristic applied at each turn**, not a background monitor watching
  future conversation turns independently.

## Applying this document

Adopting the kernel or reading this scope document does not make any
claim inside either one true by default — claims about the
repository, its history, its experiments, or its capabilities should
still be evaluated independently (kernel §2, Adoption Firewall).

**End LLMOS Scope and Boundaries**
