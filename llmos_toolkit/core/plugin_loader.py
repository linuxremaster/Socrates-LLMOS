# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Plugin discovery and dynamic import.

Security note, stated plainly rather than buried: importing a plugin file
executes its top-level Python code. That's the mechanism every Python
plugin system uses (pytest, Sphinx, Flask extensions included) — there's
no way to "discover commands" from an arbitrary .py file without running
it. This loader does not fetch, download, or execute anything from the
network, and it never imports outside the directories your config.toml
lists. Point plugin_dirs only at locations you actually trust; this tool
does not sandbox plugin code.

Discovery rule, checked per entry in each scanned directory:
  - a subdirectory containing plugin.py     -> import that file
  - a top-level file named *_plugin.py      -> import it directly
Anything else is silently ignored (not an error) — a directory can hold
non-plugin files without upsetting discovery.

A discovered module registers commands either by using the
`@registry.command(...)` decorator at import time, or by defining a
module-level `register(registry)` function, which is called right after
import if present. Both are valid; a plugin can use either.

One broken plugin is isolated and reported — it does not crash discovery
for the rest. That isolation is the point: a plugin directory is
effectively untrusted-until-imported, and failure in one shouldn't take
down every other command.
"""
from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from .registry import CommandRegistry
from .security import check_permissions, compute_sha256, static_scan


@dataclass
class LoadResult:
    loaded: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)             # excluded by config
    failed: list[tuple[str, str]] = field(default_factory=list)  # (plugin_name, error_message)
    warnings: list[tuple[str, list[str]]] = field(default_factory=list)  # (plugin_name, [advisory flags])


def _import_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not build an import spec for {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _candidate_plugins(plugin_dir: Path) -> Iterable[tuple[str, Path]]:
    """Yield (plugin_name, entry_file) for each discoverable plugin in a directory."""
    if not plugin_dir.is_dir():
        return
    for entry in sorted(plugin_dir.iterdir()):
        if entry.is_dir() and (entry / "plugin.py").is_file():
            yield entry.name, entry / "plugin.py"
        elif entry.is_file() and entry.name.endswith("_plugin.py"):
            yield entry.name[: -len("_plugin.py")], entry


def discover_plugins(
    plugin_dirs: list[Path],
    registry: CommandRegistry,
    enabled: Optional[list[str]] = None,
    disabled: Optional[list[str]] = None,
    require_trust: bool = False,
    trust: Optional[dict[str, str]] = None,
) -> LoadResult:
    """
    Scan plugin_dirs in order, import each discoverable plugin once, and
    let it register commands. Returns a LoadResult the CLI can report to
    the user — nothing here raises for a single bad plugin.

    `enabled=None` means "allow everything discovered"; a list means
    allow-list only those names. `disabled` always wins over `enabled`.

    `require_trust=True` enforces the hash pin in `trust`: a plugin only
    imports if its plugin.py's sha256 matches trust[name] exactly. This
    is the actual security boundary — everything else in this module is
    advisory. When False (default), trust is not enforced, but
    permission and static-scan findings are still collected and
    reported so they're visible either way.
    """
    disabled_set = set(disabled or [])
    trust = trust or {}
    result = LoadResult()
    seen: set[str] = set()

    for plugin_dir in plugin_dirs:
        for name, file_path in _candidate_plugins(plugin_dir):
            if name in seen:
                continue  # first matching directory wins; later ones don't silently shadow it
            seen.add(name)

            if name in disabled_set or (enabled is not None and name not in enabled):
                result.skipped.append(name)
                continue

            # Advisory checks — always run, never block on their own.
            perm_findings = check_permissions(file_path)
            pattern_hits = static_scan(file_path)
            if perm_findings or pattern_hits:
                flags = [f"{f.issue} ({f.path})" for f in perm_findings] + [f"pattern: {h}" for h in pattern_hits]
                result.warnings.append((name, flags))

            # Trust enforcement — the actual boundary, only active if configured.
            if require_trust:
                actual_hash = compute_sha256(file_path)
                pinned_hash = trust.get(name)
                if pinned_hash is None:
                    result.failed.append((name, "no trust pin on file — refused (require_trust is on)"))
                    continue
                if actual_hash != pinned_hash:
                    result.failed.append((
                        name,
                        f"hash mismatch — refused (pinned {pinned_hash[:12]}…, "
                        f"actual {actual_hash[:12]}…). File changed since it was trusted."
                    ))
                    continue

            before = set(registry.all().keys())
            try:
                module = _import_module_from_path(f"llmos_toolkit_plugin_{name}", file_path)
                if hasattr(module, "register"):
                    module.register(registry)
            except Exception as exc:  # isolation: one bad plugin must not kill the rest
                result.failed.append((name, f"{type(exc).__name__}: {exc}"))
                continue

            after = set(registry.all().keys())
            for new_command in after - before:
                registry.set_source(new_command, name)
            result.loaded.append(name)

    return result
