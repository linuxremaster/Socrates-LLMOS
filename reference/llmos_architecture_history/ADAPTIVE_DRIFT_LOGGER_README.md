<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Adaptive Drift Logger

This logger is based on the supplied project context, which identifies five
observed drift classes: growth/bloat, semantic, cross-artifact,
embedded-vs-standalone, and numbering/structural drift. It also records that
generic proximity matching produced false-positive floods, so cross-reference
checks are restricted to labelled reference fields.

The logger deliberately does **not** promote textual similarity to semantic
equivalence. Semantic changes are emitted as review findings.

Self-adaptation is conservative: repeated observations are counted, but a
detector/signature is promoted only after explicit external confirmation.
This prevents the logger from learning its own false positives as truth.

Usage:

    python adaptive_drift_logger.py path/to/kernel.md

Multiple artifacts:

    python adaptive_drift_logger.py kernel.md adapter.md global_check.md

The first run establishes a baseline. Later runs compare against the stored
snapshot/baseline. Exit codes:
- 0: no findings
- 1: findings requiring review
- 2: high-severity finding requiring review

State is stored in `.drift_state.json`; the append-only audit history is
`drift_audit.jsonl`.
