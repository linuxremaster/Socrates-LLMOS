<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Socrates LLMOS

**Alpha.** An epistemic-discipline kernel and toolkit for
working with LLMs — evidence tiers, cross-model audit verification,
decision-finality process, and a relay console for multi-instance
work. Household-scale project, alpha, actively developed. Current
version: see [git tags](../../tags) or [`docs/CHANGELOG.md`](./docs/CHANGELOG.md)
— not duplicated here, since a hardcoded number in prose reliably goes
stale on every future bump (confirmed: this file said "v0.6.0-alpha"
through three subsequent releases before being caught).

**Read [`WHAT_THIS_IS_BUILT_ON.md`](./WHAT_THIS_IS_BUILT_ON.md) first.**
It names what this project can't enforce, and what actually does.

## What's here

- **`kernel/`** — the actual reasoning-discipline documents. Start
  with `HCF_LLMOS_Kernel_v1.3.6-C.md`.
- **`llmos_toolkit/`** — a Python CLI (`llmos --list-commands`) for
  drift tracking, secret scanning, behavioral observation logging,
  and audit tooling.
- **`projects/relay_console/`** — a browser-based multi-instance LLM
  relay tool (manual/async and API-based/sync modes).
- **`docs/`** — narrative documentation; see `docs/README.md` for the
  full directory guide and `docs/CHANGELOG.md` for version history.
- **`reference/`** — archived historical material, not actively
  maintained.

## Governance and scope

- [`WHAT_THIS_IS_BUILT_ON.md`](./WHAT_THIS_IS_BUILT_ON.md) — real
  provider Usage Policies and safety frameworks, verified current as
  of last check.
- [`docs/REGULATORY_SCOPE_NOTE.md`](./docs/REGULATORY_SCOPE_NOTE.md)
  — factual EU/US AI-law scope (not legal advice).
- [`EXECUTION_BOUNDARY_UPDATES.md`](./EXECUTION_BOUNDARY_UPDATES.md)
  — log of checked provider/regulatory changes.
- [`KERNEL_ADOPTION_TRACKING.md`](./KERNEL_ADOPTION_TRACKING.md) —
  which kernel principles have logged evidence of real use.

## Install

```
pip install -e . --break-system-packages --no-build-isolation
llmos --list-commands
```

## License

MPL 2.0 — see [`LICENSE`](./LICENSE). GPL-compatible by default (no
opt-out notice attached); see the kernel's Cross-Model Provenance
section for the reasoning.

**No warranty, no guarantee of fitness for any purpose.** This is an
alpha-stage personal project, not a certified or audited product.
