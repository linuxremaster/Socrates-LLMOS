# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Minimal example plugin — demonstrates decorator-style registration, the
alternative to growth_budget's explicit register(registry) style. Both
are valid: a single simple command reads cleanly as a decorator; a
plugin with several related commands or custom argparse setup often
reads more cleanly with an explicit register() function instead.

This is the template to copy for a new one-command plugin: drop a
directory under plugins/ with a plugin.py that looks like this, and it's
discovered and wired into the CLI automatically on the next run — no
edits to any other file required.
"""
from __future__ import annotations

import argparse

from llmos_toolkit.core.registry import registry


def _configure(p: argparse.ArgumentParser) -> None:
    p.add_argument("name", nargs="?", default="world")


@registry.command("hello", help="Print a greeting (example plugin)", configure_parser=_configure)
def cmd_hello(args: argparse.Namespace) -> int:
    print(f"Hello, {args.name}! (this command came from the example_hello plugin)")
    return 0
