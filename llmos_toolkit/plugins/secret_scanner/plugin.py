# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Secret Scanner plugin — regex + Shannon-entropy heuristics for hardcoded
credentials. Advisory, same honesty standard as core/security.py's
static_scan: flags shaped-like-a-secret strings for human review, not a
guarantee nothing was missed.

Self-exclusion: this plugin's own directory is excluded from every
check, including the "sensitive filename" heuristic. Without that, a
file named secret_scanner.py trivially flags itself on every single
run, since "secret" is a substring of its own filename — confirmed as
a real bug in the original draft before this fix.
"""
from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Any, Optional

from llmos_toolkit.core.paths import PROJECT_ROOT

SECRET_PATTERNS = [
    (r"(?i)api[_-]?key\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?", "API Key"),
    (r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}", "Bearer Token"),
    (r"sk-[a-zA-Z0-9]{32,}", "OpenAI-style Key"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----", "Private Key"),
]

IGNORE_DIRS = {".git", "__pycache__", ".venv", "venv", ".egg-info"}
IGNORE_EXTS = {".png", ".jpg", ".jpeg", ".db", ".sqlite", ".pyc", ".zip"}

_SELF_DIR = Path(__file__).resolve().parent  # plugins/secret_scanner/ — excluded entirely
_TESTS_DIR_NAME = "tests"  # top-level tests/ — excluded: fixtures deliberately contain fake-secret-shaped strings


def calculate_entropy(data: str) -> float:
    if not data:
        return 0.0
    entropy = 0.0
    for char in set(data):
        p_x = data.count(char) / len(data)
        entropy -= p_x * math.log2(p_x)
    return entropy


def _is_self(file_path: Path) -> bool:
    resolved = file_path.resolve()
    if resolved == _SELF_DIR or _SELF_DIR in resolved.parents:
        return True
    return any(part == _TESTS_DIR_NAME for part in resolved.parts)


def scan_file(file_path: Path, project_root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if _is_self(file_path):
        return findings

    name_lower = file_path.name.lower()
    template_suffixes = (".example", ".sample", ".template", ".dist")
    is_template = any(name_lower.endswith(suffix) for suffix in template_suffixes)

    sensitive_name_markers = (
        "secret", "credential", ".env", ".pem", "id_rsa", "id_ed25519",
        ".npmrc", ".netrc", ".pgpass", "known_hosts",
    )
    if not is_template and any(marker in name_lower for marker in sensitive_name_markers):
        findings.append({
            "file": str(file_path.relative_to(project_root)),
            "line": 0, "type": "Sensitive File Name", "match": file_path.name,
        })

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    for line_num, line in enumerate(content.splitlines(), start=1):
        for pattern, label in SECRET_PATTERNS:
            if re.search(pattern, line):
                findings.append({
                    "file": str(file_path.relative_to(project_root)),
                    "line": line_num, "type": label, "match": line.strip()[:60] + "...",
                })
        url_spans = [m.span() for m in re.finditer(r"https?://\S+", line)]
        code_spans = [m.span() for m in re.finditer(r"`[^`]+`", line)]
        skip_spans = url_spans + code_spans
        for word in re.finditer(r"\b[A-Za-z0-9_\-]{32,}\b", line):
            if any(word.start() >= s and word.end() <= e for s, e in skip_spans):
                continue  # inside a URL or `backtick code/filename span` — high-entropy by nature, not a secret
            token = word.group(0)
            if calculate_entropy(token) > 4.5:
                findings.append({
                    "file": str(file_path.relative_to(project_root)),
                    "line": line_num, "type": "High Entropy Token", "match": token[:15] + "...",
                })
    return findings


def run_secret_scan(target_dir: Optional[Path] = None) -> dict[str, Any]:
    target_dir = target_dir or PROJECT_ROOT
    all_findings: list[dict[str, Any]] = []
    scanned_files = 0

    for path in target_dir.rglob("*"):
        if path.is_dir() or any(p in path.parts for p in IGNORE_DIRS):
            continue
        if path.suffix in IGNORE_EXTS:
            continue
        if _is_self(path):
            continue
        scanned_files += 1
        all_findings.extend(scan_file(path, target_dir))

    return {
        "status": "FAIL" if all_findings else "PASS",
        "scanned_files": scanned_files,
        "findings_count": len(all_findings),
        "findings": all_findings,
    }


def _configure_scan(p: argparse.ArgumentParser) -> None:
    p.add_argument("--dir", default=None, help="Directory to scan (default: project root)")


def cmd_scan(args: argparse.Namespace) -> int:
    target = Path(args.dir) if args.dir else PROJECT_ROOT
    result = run_secret_scan(target)
    print(f"Scanned {result['scanned_files']} file(s). Status: {result['status']}")
    for f in result["findings"]:
        print(f"  [{f['type']}] {f['file']}:{f['line']}  {f['match']}")
    return 0 if result["status"] == "PASS" else 1


def register(registry) -> None:
    registry.register("scan-secrets", cmd_scan,
                       help="Scan the project for hardcoded credentials (regex + entropy heuristics)",
                       configure_parser=_configure_scan, source="secret_scanner")
