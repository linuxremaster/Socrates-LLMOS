# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Config loading. Reads config.toml at the package root; falls back to
sane defaults (scan the bundled plugins/ directory, nothing disabled) if
the file is missing.

Uses tomllib (stdlib since Python 3.11) — this toolkit targets 3.11+.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.toml"


@dataclass
class ToolkitConfig:
    plugin_dirs: list[Path] = field(default_factory=list)
    enabled: Optional[list[str]] = None   # None = allow every discovered plugin
    disabled: list[str] = field(default_factory=list)
    require_trust: bool = False           # if True, a plugin must match `trust` to load
    trust: dict[str, str] = field(default_factory=dict)  # plugin name -> expected sha256 hex

    @classmethod
    def load(cls, path: Path = DEFAULT_CONFIG_PATH) -> "ToolkitConfig":
        root = path.resolve().parent

        if not path.is_file():
            return cls(plugin_dirs=[root / "plugins"])

        data = tomllib.loads(path.read_text(encoding="utf-8"))
        raw_dirs = data.get("plugin_dirs", ["plugins"])
        plugin_dirs = [
            Path(d) if Path(d).is_absolute() else (root / d)
            for d in raw_dirs
        ]
        return cls(
            plugin_dirs=plugin_dirs,
            enabled=data.get("enabled"),
            disabled=data.get("disabled", []),
            require_trust=data.get("require_trust", False),
            trust=data.get("trust", {}),
        )
