# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Audit All plugin — secret scan + cryptographic kernel verification in
one pass. The kernel check does a real SHA-256 comparison against the
pin recorded in state/kernel_pins.json (same file/format `pin-kernel`
writes) — not a file-existence check. A stub that always reports PASS
regardless of tampering is worse than no check at all; that was the bug
in the original draft this replaces.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from llmos_toolkit.core.paths import get_default_kernel, get_state_path
from llmos_toolkit.core.security import compute_sha256
from llmos_toolkit.plugins.secret_scanner.plugin import run_secret_scan


def _check_kernel_integrity(kernel_path: Path) -> dict[str, Any]:
    pins_file = get_state_path("kernel_pins.json")
    if not pins_file.exists():
        return {"status": "FAIL", "error": f"No kernel_pins.json at {pins_file} — run pin-kernel first."}

    pins = json.loads(pins_file.read_text(encoding="utf-8"))
    label = kernel_path.name
    pin = pins.get(label)
    if pin is None:
        return {"status": "FAIL", "error": f"'{label}' is not pinned — run pin-kernel first."}
    if not kernel_path.exists():
        return {"status": "FAIL", "error": f"Kernel file not found: {kernel_path}"}

    current_hash = compute_sha256(kernel_path)
    if current_hash == pin["sha256"]:
        return {"status": "PASS", "kernel_file": label, "sha256": current_hash[:16] + "…"}
    return {
        "status": "FAIL", "kernel_file": label,
        "error": "Hash mismatch against pinned baseline.",
        "pinned": pin["sha256"][:16] + "…", "current": current_hash[:16] + "…",
    }


def _check_governance_docs_present() -> dict[str, Any]:
    """Advisory only, never blocking overall_pass -- flags if scope/
    governance docs go missing, same visible-not-destructive pattern as
    the kernel pin check. Deleting these files breaks nothing and harms
    no one; it just means this warning fires, honestly, every time."""
    from llmos_toolkit.core.paths import PROJECT_ROOT
    required = [
        PROJECT_ROOT / "WHAT_THIS_IS_BUILT_ON.md",
        PROJECT_ROOT / "Execution Boundary Updates.md",
        PROJECT_ROOT / "docs" / "REGULATORY_SCOPE_NOTE.md",
        PROJECT_ROOT / "docs" / "LLMOS_SCOPE_AND_BOUNDARIES.md",
    ]
    missing = [str(p.relative_to(PROJECT_ROOT)) for p in required if not p.exists()]
    return {"missing": missing}


def cmd_audit_all(args: argparse.Namespace) -> int:
    print("=" * 60)
    print("      SOCRATES LLMOS — UNIFIED SYSTEM AUDIT PASS")
    print("=" * 60)

    overall_pass = True

    print("\n[1/3] Running Secret & Credential Audit...")
    secret_results = run_secret_scan()
    if secret_results["status"] == "FAIL":
        overall_pass = False
        print(f"  FAILED: {secret_results['findings_count']} potential secret(s) found.")
        for f in secret_results["findings"]:
            print(f"    [{f['type']}] {f['file']}:{f['line']}")
    else:
        print(f"  PASSED ({secret_results['scanned_files']} files clean)")

    print("\n[2/3] Verifying Kernel Cryptographic Pin...")
    kernel_path = Path(args.kernel) if args.kernel else get_default_kernel()
    kernel_result = _check_kernel_integrity(kernel_path)
    if kernel_result["status"] == "FAIL":
        overall_pass = False
        print(f"  FAILED: {kernel_result.get('error', 'unknown')}")
        if "pinned" in kernel_result:
            print(f"    pinned:  {kernel_result['pinned']}")
            print(f"    current: {kernel_result['current']}")
    else:
        print(f"  PASSED ({kernel_result['kernel_file']}, {kernel_result['sha256']})")

    print("\n[3/3] Checking Governance/Scope Documentation Presence (advisory only)...")
    gov_result = _check_governance_docs_present()
    if gov_result["missing"]:
        print(f"  ADVISORY: missing {len(gov_result['missing'])} governance doc(s) -- "
              "this does NOT fail the audit or block anything, it's a visible reminder only:")
        for m in gov_result["missing"]:
            print(f"    {m}")
    else:
        print("  Present.")

    print("\n" + "=" * 60)
    print(f" FINAL AUDIT STATUS: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 60)

    return 0 if overall_pass else 1


def _configure_audit_all(p: argparse.ArgumentParser) -> None:
    p.add_argument("--kernel", help="Kernel file to verify (default: auto-detected)")


def register(registry) -> None:
    registry.register("audit-all", cmd_audit_all,
                       help="Run secret scan + cryptographic kernel verification in one pass",
                       configure_parser=_configure_audit_all, source="audit_all")
