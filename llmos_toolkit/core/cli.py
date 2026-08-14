# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Entry point. Loads config, discovers plugins, builds an argparse CLI from
whatever commands got registered at runtime, and dispatches.

Usage:
    python -m llmos_toolkit <command> [args...]
    python -m llmos_toolkit --list-commands
    python -m llmos_toolkit --list-commands --verbose   (also show failure details)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import ToolkitConfig
from .paths import get_state_path
from .plugin_loader import LoadResult, discover_plugins
from .registry import registry, RESERVED_COMMAND_NAMES
from .security import check_permissions, compute_sha256, static_scan

KERNEL_PIN_FILE = get_state_path("kernel_pins.json")


def _print_discovery_report(result: LoadResult, verbose: bool) -> None:
    print(f"Discovered {len(result.loaded)} plugin(s): {', '.join(result.loaded) or '(none)'}")
    if result.skipped:
        print(f"Skipped (disabled or not in enabled list): {', '.join(result.skipped)}")
    if result.failed:
        print(f"Failed to load: {', '.join(name for name, _ in result.failed)}")
        if verbose:
            for name, err in result.failed:
                print(f"  {name}: {err}")
    if result.warnings:
        print(f"Advisory findings (not blocking — see core/security.py docstring): "
              f"{', '.join(name for name, _ in result.warnings)}")
        if verbose:
            for name, flags in result.warnings:
                for flag in flags:
                    print(f"  {name}: {flag}")
    print()
    print("Available commands:")
    if not registry.all():
        print("  (none registered)")
    for name, spec in sorted(registry.all().items()):
        print(f"  {name:<15} [{spec.source}]  {spec.help}")


# ---------------------------------------------------------------------------
# Built-in security commands. These are NOT plugins and never go through the
# plugin loader or the trust gate — they're what manages that gate, so they
# must work even when every plugin is untrusted or unloadable. Wired
# directly into the argparse tree in build_parser() below.
# ---------------------------------------------------------------------------

def cmd_trust_plugin(args: argparse.Namespace) -> int:
    """Compute a plugin file's current hash and print the config.toml line to pin it."""
    path = Path(args.plugin_file)
    if not path.is_file():
        print(f"Not a file: {path}", file=sys.stderr)
        return 1
    digest = compute_sha256(path)
    print(f"sha256: {digest}")
    print()
    print("Add this to config.toml under [trust] to pin it:")
    print(f'{args.name} = "{digest}"')
    perm = check_permissions(path)
    if perm:
        print()
        print("WARNING — permission findings on this file (review before trusting):")
        for f in perm:
            print(f"  {f.issue}: {f.path}")
    return 0


def _configure_trust_plugin(p: argparse.ArgumentParser) -> None:
    p.add_argument("name", help="Plugin name as it should appear under [trust] in config.toml")
    p.add_argument("plugin_file", help="Path to the plugin's plugin.py")


def cmd_scan_plugin(args: argparse.Namespace) -> int:
    """Run the advisory permission + pattern scan against a plugin file, standalone."""
    path = Path(args.plugin_file)
    if not path.is_file():
        print(f"Not a file: {path}", file=sys.stderr)
        return 1
    perm = check_permissions(path)
    patterns = static_scan(path)
    if not perm and not patterns:
        print(f"No findings for {path}.")
        return 0
    print(f"Findings for {path}:")
    for f in perm:
        print(f"  {f.issue}: {f.path}")
    for label in patterns:
        print(f"  pattern: {label}")
    print()
    print("Reminder: this is advisory, not a security boundary (see core/security.py).")
    return 0


def _configure_scan_plugin(p: argparse.ArgumentParser) -> None:
    p.add_argument("plugin_file", help="Path to the plugin.py to scan")


def _load_kernel_pins() -> dict:
    if not KERNEL_PIN_FILE.exists():
        return {}
    return json.loads(KERNEL_PIN_FILE.read_text(encoding="utf-8"))


def _save_kernel_pins(pins: dict) -> None:
    KERNEL_PIN_FILE.write_text(json.dumps(pins, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cmd_pin_kernel(args: argparse.Namespace) -> int:
    """Record the current sha256 of a kernel file as its trusted baseline."""
    path = Path(args.kernel_file)
    if not path.is_file():
        print(f"Not a file: {path}", file=sys.stderr)
        return 1
    digest = compute_sha256(path)
    pins = _load_kernel_pins()
    label = args.label or path.name
    pins[label] = {
        "path": str(path),
        "sha256": digest,
        "pinned_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_kernel_pins(pins)
    print(f"Pinned '{label}' -> {digest[:16]}… ({KERNEL_PIN_FILE})")
    return 0


def _configure_pin_kernel(p: argparse.ArgumentParser) -> None:
    p.add_argument("kernel_file")
    p.add_argument("--label", help="Name to store the pin under (default: filename)")


def cmd_verify_kernel(args: argparse.Namespace) -> int:
    """Compare a kernel file's current hash against its pinned baseline."""
    path = Path(args.kernel_file)
    if not path.is_file():
        print(f"Not a file: {path}", file=sys.stderr)
        return 1
    pins = _load_kernel_pins()
    label = args.label or path.name
    pin = pins.get(label)
    if pin is None:
        print(f"UNPINNED: no baseline recorded for '{label}'. Run pin-kernel first.")
        return 1
    current = compute_sha256(path)
    if current == pin["sha256"]:
        print(f"MATCH: {label} unchanged since pinned at {pin['pinned_at']}.")
        return 0
    print(f"DRIFT DETECTED: {label} does not match its pinned baseline.")
    print(f"  pinned  ({pin['pinned_at']}): {pin['sha256'][:16]}…")
    print(f"  current:                    {current[:16]}…")
    print("  This means the file changed since it was last pinned — expected after a")
    print("  legitimate edit, worth investigating if not.")
    return 1


def _configure_verify_kernel(p: argparse.ArgumentParser) -> None:
    p.add_argument("kernel_file")
    p.add_argument("--label", help="Name the pin was stored under (default: filename)")


def cmd_kernel_hook(args: argparse.Namespace) -> int:
    """The actual kernel<->toolkit integration point: runs kernel integrity
    verification (pin-based, from core/security.py) and the adaptive drift
    logger (five-class, from adaptive_drift_logger.py) against the same
    file set, in one call, with one combined exit code.

    This is a literal script — it does nothing on its own. Something real
    has to invoke it: you, running it by hand; a git pre-commit hook (see
    hooks/pre-commit in this package); or a cron job. There is no
    mechanism by which reading the kernel document causes this to run —
    that would contradict the kernel's own Execution Boundary.
    """
    import importlib.util as _ilu
    adl_path = Path(__file__).resolve().parent.parent / "adaptive_drift_logger.py"
    spec = _ilu.spec_from_file_location("adaptive_drift_logger_impl", adl_path)
    adl = _ilu.module_from_spec(spec)
    sys.modules["adaptive_drift_logger_impl"] = adl  # required before exec_module — see plugin.py's same fix
    spec.loader.exec_module(adl)

    overall_exit = 0

    print("== Kernel integrity (pin-based) ==")
    pins = _load_kernel_pins()
    for f in args.kernel_files:
        path = Path(f)
        label = path.name
        pin = pins.get(label)
        if pin is None:
            print(f"  UNPINNED: {label} — run pin-kernel before this hook can verify it.")
            overall_exit = max(overall_exit, 1)
            continue
        current = compute_sha256(path)
        if current == pin["sha256"]:
            print(f"  MATCH: {label}")
        else:
            print(f"  DRIFT DETECTED: {label} does not match its pinned baseline.")
            overall_exit = max(overall_exit, 2)

    print()
    print("== Adaptive drift log (five-class) ==")
    drift_exit = adl.cmd_run(args.kernel_files, rebaseline=False)
    overall_exit = max(overall_exit, drift_exit)

    print()
    print(f"kernel-hook: {'PASS' if overall_exit == 0 else f'exit {overall_exit}'}")
    return overall_exit


def _configure_kernel_hook(p: argparse.ArgumentParser) -> None:
    p.add_argument("kernel_files", nargs="+", help="Kernel/policy markdown files to check")


_BUILTIN_COMMANDS = {
    "trust-plugin": (cmd_trust_plugin, _configure_trust_plugin, "Compute a plugin's hash and print its trust-pin line"),
    "scan-plugin": (cmd_scan_plugin, _configure_scan_plugin, "Run the advisory security scan on a plugin file"),
    "pin-kernel": (cmd_pin_kernel, _configure_pin_kernel, "Record a kernel file's current hash as its trusted baseline"),
    "verify-kernel": (cmd_verify_kernel, _configure_verify_kernel, "Check a kernel file against its pinned baseline"),
    "kernel-hook": (cmd_kernel_hook, _configure_kernel_hook, "Run integrity + adaptive drift check together, one exit code"),
}

assert set(_BUILTIN_COMMANDS.keys()) == RESERVED_COMMAND_NAMES, (
    "_BUILTIN_COMMANDS keys and registry.RESERVED_COMMAND_NAMES have drifted apart — "
    "update both together, they must name the same commands."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llmos-toolkit", description=__doc__)
    parser.add_argument("--list-commands", action="store_true", help="List discovered commands and exit")
    parser.add_argument("--verbose", action="store_true", help="Show plugin load failure details")
    sub = parser.add_subparsers(dest="command")

    for cmd_name, (_handler, configure, help_text) in _BUILTIN_COMMANDS.items():
        p = sub.add_parser(cmd_name, help=f"[builtin] {help_text}")
        configure(p)

    for name, spec in sorted(registry.all().items()):
        p = sub.add_parser(name, help=f"[{spec.source}] {spec.help}")
        if spec.configure_parser:
            spec.configure_parser(p)
        else:
            p.add_argument("args", nargs=argparse.REMAINDER)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    config = ToolkitConfig.load()
    result = discover_plugins(
        config.plugin_dirs, registry,
        enabled=config.enabled, disabled=config.disabled,
        require_trust=config.require_trust, trust=config.trust,
    )

    verbose = "--verbose" in argv
    if "--list-commands" in argv:
        _print_discovery_report(result, verbose)
        return 0

    if result.failed and verbose:
        for name, err in result.failed:
            print(f"[plugin load failed] {name}: {err}", file=sys.stderr)

    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    if args.command in _BUILTIN_COMMANDS:
        handler, _configure, _help = _BUILTIN_COMMANDS[args.command]
        return handler(args) or 0

    spec = registry.get(args.command)
    if spec is None:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1

    return spec.handler(args) or 0
