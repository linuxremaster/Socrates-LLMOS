# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Sync plugin — EMPTY SLOT. No sync logic exists yet. This file registers
one command (`sync-status`) that reports the slot is unconfigured. It
exists so a future sync backend has a defined place to be added without
touching core/, not because sync is implemented.

Why this is a plugin and not built into core/: sync is optional and
swappable (manual today via git/Syncthing/whatever you already trust;
maybe real-time later), and nothing else in the toolkit depends on it
existing. That's the actual test for plugin-vs-core — see core/cli.py's
built-ins (trust-plugin, verify-kernel, kernel-hook) for the opposite
case: those manage the trust gate itself, so they can't be plugins
without creating a circular dependency.

What a real sync backend would need to do, when one is actually built —
NOT built now, this is a design note for later, not a commitment:

  - Treat every toolkit state file as the unit of sync: growth_ledger.jsonl,
    .drift_state.json, token_ledger.jsonl, kernel_pins.json, drift_rules.json,
    and any relay-session log. All are already plain JSON/JSONL — no new
    format needed.
  - Default transport: whatever directory-sync mechanism the user already
    trusts (git repo, Syncthing, Dropbox, etc.) — the toolkit doesn't need
    to know sync is happening, it just reads/writes files. This plugin's
    job would be detecting conflicts (two devices wrote the same file
    differently) and merging append-only logs safely, not moving bytes
    between devices — that part is already solved by existing tools.
  - Real-time sync, if ever wanted, is a different and much larger scope
    (a running service, not a CLI command) — do not build it into this
    plugin's shape without treating it as its own separate project.

register(registry) intentionally adds nothing beyond the status command
below. Adding real sync logic here without a concrete, current need would
be exactly the kind of unjustified growth growth_budget.py exists to
catch.
"""
from __future__ import annotations

import argparse


def cmd_status(_args: argparse.Namespace) -> int:
    print("sync: two layers exist.")
    print("1. git_sync plugin (real, tested): git-sync-status / git-sync-pull /")
    print("   git-sync-push. One-shot commands, not a live connection — see")
    print("   git_sync/plugin.py's docstring for the explicit not-live-not-persistent")
    print("   design rule.")
    print("2. This slot (sync-status) stays as the general pointer: for anything")
    print("   git_sync doesn't cover, put state files in a directory you already")
    print("   sync (Syncthing, Dropbox, etc.) — no toolkit code required for that.")
    return 0


def register(registry) -> None:
    registry.register("sync-status", cmd_status,
                       help="Report sync status (git_sync is real; this is the general pointer)",
                       source="sync")
