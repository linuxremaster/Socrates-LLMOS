# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Security utilities for the plugin loader and kernel-file handling.

Scope, stated honestly: these are hardening measures appropriate for a
local, single-user CLI tool with a dynamic-import plugin mechanism. They
are NOT a sandbox. A plugin that passes every check here still runs with
full process privileges once imported — nothing in this file stops a
trusted-but-malicious plugin from doing anything Python itself can do.
What this DOES meaningfully change:

  - an unreviewed file dropped into plugins/ no longer auto-executes
    silently when trust mode is on — it's refused unless its hash
    matches a value you explicitly pinned. This is the real control.
  - group/world-writable plugin sources are flagged: on a shared
    machine, either is a local-privilege-escalation path (another
    account edits the file, your next run silently executes it).
  - a lightweight pattern scan flags plugins using subprocess/network/
    eval-family calls, as an advisory signal for human review.

The static pattern scan is explicitly NOT a security boundary — it's
regex-based and trivially bypassed (string building, base64, getattr
indirection, etc.). Treat its output as "worth a human look," never as
"cleared." The only actual enforcement mechanism here is the hash pin.
"""
from __future__ import annotations

import hashlib
import re
import stat
from dataclasses import dataclass
from pathlib import Path

SUSPICIOUS_PATTERNS: dict[str, re.Pattern] = {
    "subprocess": re.compile(r"\bimport\s+subprocess\b|\bsubprocess\."),
    "os.system": re.compile(r"\bos\.system\("),
    "eval(": re.compile(r"\beval\("),
    "exec(": re.compile(r"\bexec\("),
    "dynamic __import__": re.compile(r"__import__\("),
    "network: socket": re.compile(r"\bimport\s+socket\b"),
    "network: urllib": re.compile(r"\bimport\s+urllib\b|\burllib\."),
    "network: requests": re.compile(r"\bimport\s+requests\b"),
    "network: http.client": re.compile(r"\bimport\s+http\.client\b"),
}


def compute_sha256(path: Path) -> str:
    """Full-length hex digest — used for trust pins (unlike the 12-char
    truncated hash growth_budget.py uses for readable diffs, a trust pin
    needs the full digest to actually mean something)."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kernel_pin_key(path: Path) -> str:
    """The ONE canonical identity for kernel-pin purposes, used
    everywhere a pin gets written or checked (pin-kernel, verify-kernel,
    kernel-hook, audit-all). Real bug fixed 2026-08-17: pin-kernel and
    audit-all had already been fixed to use the resolved path, but
    verify-kernel and kernel-hook still separately computed path.name
    (basename only) -- an internal inconsistency where a normal
    pin-then-verify workflow could report UNPINNED on a file that was
    just pinned. Centralizing into one function is what actually
    prevents this class of drift from recurring a third time, not
    patching each call site individually.

    Second real bug fixed 2026-08-20, found by external audit: using
    str(path.resolve()) -- an ABSOLUTE path -- meant a pin written on
    one machine/unpack location was permanently unusable on any other,
    since kernel_pins.json travels with the project (it's gitignored,
    but zip -r doesn't respect .gitignore, so it ships anyway) while
    the absolute path it was keyed to does not. Confirmed via direct
    test: a fresh unpack to a different directory reported the correctly
    -pinned, unmodified kernel as UNPINNED. Now keyed to a path relative
    to PROJECT_ROOT instead -- travels correctly with the project,
    still fully collision-resistant (two files sharing a basename in
    different subdirectories still get distinct relative paths)."""
    from llmos_toolkit.core.paths import PROJECT_ROOT
    resolved = path.resolve()
    try:
        rel = resolved.relative_to(PROJECT_ROOT.resolve())
        return rel.as_posix()
    except ValueError:
        # Genuinely outside the project (e.g. a file in /tmp during a
        # test) -- absolute path is the only correct identity there,
        # same portability caveat as before applies, but that's an
        # honest reflection of the file's real location, not a bug.
        return resolved.as_posix()


@dataclass
class PermissionFinding:
    path: str
    issue: str


def check_permissions(path: Path) -> list[PermissionFinding]:
    """Flag a group/world-writable plugin file or its parent directory."""
    findings: list[PermissionFinding] = []
    for p in (path, path.parent):
        try:
            mode = p.stat().st_mode
        except OSError:
            continue
        if mode & stat.S_IWGRP:
            findings.append(PermissionFinding(str(p), "group-writable"))
        if mode & stat.S_IWOTH:
            findings.append(PermissionFinding(str(p), "world-writable"))
    return findings


def static_scan(path: Path) -> list[str]:
    """Advisory only — see module docstring. Returns matched pattern labels."""
    text = path.read_text(encoding="utf-8", errors="replace")
    return [label for label, pattern in SUSPICIOUS_PATTERNS.items() if pattern.search(text)]
