# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Command registry — the single source of truth for what commands exist.

Plugins register commands here one of two ways:

  1. Decorator style (simplest, for a single command):
         from llmos_toolkit.core.registry import registry

         @registry.command("hello", help="Say hello")
         def cmd_hello(args):
             print("hi")
             return 0

  2. Explicit style (for plugins with several related commands, or that
     want to build argparse config in one place — this is how the
     growth_budget plugin does it):
         def register(registry):
             registry.register("check", cmd_check, help="...", configure_parser=...)
             registry.register("check-dir", cmd_check_dir, help="...")

The registry itself doesn't know or care where a plugin came from or how
it was loaded — that's the plugin loader's job. It only tracks
name -> handler, and refuses silent collisions.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class CommandSpec:
    name: str
    handler: Callable[[argparse.Namespace], Optional[int]]
    help: str = ""
    configure_parser: Optional[Callable[[argparse.ArgumentParser], None]] = None
    source: str = "unknown"  # which plugin registered this; filled in by the loader


# Command names reserved for built-in CLI commands (see core/cli.py's
# _BUILTIN_COMMANDS). Defined here, once, so both the loader (which
# refuses plugin collisions with these) and the CLI (which wires them up)
# read from the same list instead of two lists drifting apart.
RESERVED_COMMAND_NAMES = {"trust-plugin", "scan-plugin", "pin-kernel", "verify-kernel", "kernel-hook"}


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, CommandSpec] = {}

    def command(self, name: str, help: str = "", configure_parser=None):
        """Decorator form. See module docstring."""
        def wrapper(func: Callable[[argparse.Namespace], Optional[int]]):
            self.register(name, func, help=help, configure_parser=configure_parser)
            return func
        return wrapper

    def register(
        self,
        name: str,
        handler: Callable[[argparse.Namespace], Optional[int]],
        help: str = "",
        configure_parser=None,
        source: str = "unknown",
    ) -> None:
        if name in RESERVED_COMMAND_NAMES:
            raise ValueError(
                f"Command '{name}' is reserved for a built-in CLI command "
                f"and cannot be registered by a plugin ('{source}')."
            )
        if name in self._commands:
            existing = self._commands[name]
            raise ValueError(
                f"Command '{name}' is already registered by plugin "
                f"'{existing.source}' — refusing to silently let "
                f"'{source}' overwrite it. Rename one of the commands."
            )
        self._commands[name] = CommandSpec(
            name=name, handler=handler, help=help,
            configure_parser=configure_parser, source=source,
        )

    def set_source(self, name: str, source: str) -> None:
        if name in self._commands:
            self._commands[name].source = source

    def all(self) -> dict[str, CommandSpec]:
        return dict(self._commands)

    def get(self, name: str) -> Optional[CommandSpec]:
        return self._commands.get(name)

    def clear(self) -> None:
        """Mainly for tests — reset the registry between runs."""
        self._commands.clear()


# Module-level singleton — plugins import this directly.
registry = CommandRegistry()
