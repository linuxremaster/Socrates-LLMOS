# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Centralized path resolution — separate module from core/config.py on
purpose. An earlier draft of this idea proposed replacing config.py
outright; that would have silently destroyed ToolkitConfig (plugin_dirs,
require_trust, the trust manifest), which cli.py depends on directly.
This module owns filesystem layout only; config.py still owns plugin/
trust configuration. Two concerns, two files.

Env vars override the defaults when set, for anyone running outside the
standard llmos_project/ layout.
"""
from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent.parent  # .../llmos_toolkit
_DEFAULT_PROJECT_ROOT = PACKAGE_DIR.parent             # .../llmos_project
PROJECT_ROOT = Path(os.getenv("LLMOS_PROJECT_ROOT", str(_DEFAULT_PROJECT_ROOT)))

STATE_DIR = Path(os.getenv("LLMOS_STATE_DIR", str(PROJECT_ROOT / "state")))
KERNEL_DIR = Path(os.getenv("LLMOS_KERNEL_DIR", str(PROJECT_ROOT / "kernel")))
PROJECTS_DIR = Path(os.getenv("LLMOS_PROJECTS_DIR", str(PROJECT_ROOT / "projects")))
DOCS_DIR = Path(os.getenv("LLMOS_DOCS_DIR", str(PROJECT_ROOT / "docs")))
RAG_DIR = Path(os.getenv("LLMOS_RAG_DIR", str(PROJECT_ROOT / "rag")))


def get_state_path(filename: str) -> Path:
    """Ensures the state directory exists; returns the full path for a state file."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    return STATE_DIR / filename


def get_rag_path(filename: str) -> Path:
    """Ensures the RAG directory exists; returns the full path for a RAG
    artifact (index db, generated handoff doc). Kept separate from
    STATE_DIR — state/ holds integrity/audit artifacts (pins, ledgers),
    rag/ holds retrieval artifacts, so a full RAG rebuild never touches
    audit history and vice versa."""
    RAG_DIR.mkdir(parents=True, exist_ok=True)
    return RAG_DIR / filename


def get_default_kernel() -> Path:
    """Finds the active kernel file in kernel/. Falls back to the known
    current filename if the glob finds nothing."""
    if KERNEL_DIR.is_dir():
        kernels = sorted(KERNEL_DIR.glob("HCF_LLMOS_Kernel_*.md"))
        if kernels:
            return kernels[-1]
    return KERNEL_DIR / "HCF_LLMOS_Kernel_v1.3.6-C.md"
