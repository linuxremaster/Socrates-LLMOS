# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Real bugs found by an external ChatGPT audit 2026-08-20, which actually
unpacked and executed v0.7.0-alpha rather than just reviewing docs.
All three confirmed by direct trace/reproduction before fixing, not
just trusted from the report.

Honest limitation on the relay tests: pydantic/fastapi aren't
installed in this dev sandbox (no external network access to pip
install them), so RelaySession itself can't be imported and tested
directly here. These tests mirror the exact fixed algorithm using
plain dicts instead of the real Turn/pydantic models. They're real
tests of the real logic, not the real class -- worth knowing that
distinction if this suite runs somewhere the real dependencies ARE
available, where testing the actual RelaySession class directly would
be strictly better.
"""

import argparse
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


def _history_for(turns, target_slot):
    history = []
    for t in turns:
        if t["status"] not in ("approved", "sent", "complete"):
            continue
        role = "assistant" if t["from_slot"] == target_slot else "user"
        history.append({"role": role, "content": t["content"]})
    return history


def _simulate_sync_auto(n_exchanges):
    """Mirrors the fixed logic in relay_engine.py's non-ASYNC_GATED
    branch: only explicitly append pending_content on the very first
    call, since _history_for already includes it on every call after."""
    turns = []
    next_slot = "B"
    pending_content = "OPENING_MESSAGE"
    histories_sent = []
    for i in range(n_exchanges):
        target = next_slot
        history = _history_for(turns, target)
        if not turns:
            history = history + [{"role": "user", "content": pending_content}]
        histories_sent.append(list(history))
        response_content = f"resp{i + 1}"
        turns.append({"turn_number": len(turns), "from_slot": target, "content": response_content, "status": "sent"})
        next_slot = "A" if target == "B" else "B"
        pending_content = response_content
    return histories_sent, turns


class TestRelayDuplicationFix(unittest.TestCase):
    def test_sync_auto_no_duplicate_content_across_exchanges(self):
        histories, _ = _simulate_sync_auto(4)
        for i, h in enumerate(histories):
            contents = [m["content"] for m in h]
            self.assertEqual(len(contents), len(set(contents)),
                              f"call {i + 1} has duplicate content: {contents}")

    def test_turn_numbers_are_unique_and_sequential(self):
        _, turns = _simulate_sync_auto(5)
        numbers = [t["turn_number"] for t in turns]
        self.assertEqual(numbers, list(range(len(turns))))

    def test_old_logic_genuinely_reproduces_the_original_bug(self):
        """Confirms this is a real regression test, not a tautology --
        the pre-fix logic (unconditionally appending pending_content)
        actually duplicates content, matching the audit's exact
        finding: 'call 2 received resp1 twice.'"""
        turns = []
        next_slot = "B"
        pending_content = "OPENING_MESSAGE"
        second_call_history = None
        for i in range(2):
            target = next_slot
            history = _history_for(turns, target) + [{"role": "user", "content": pending_content}]
            if i == 1:
                second_call_history = history
            response_content = f"resp{i + 1}"
            turns.append({"turn_number": len(turns) + 1, "from_slot": target, "content": response_content, "status": "sent"})
            next_slot = "A" if target == "B" else "B"
            pending_content = response_content
        contents = [m["content"] for m in second_call_history]
        self.assertEqual(contents, ["resp1", "resp1"], "old logic should genuinely duplicate resp1")


class TestKernelPinPortability(unittest.TestCase):
    """Second real bug from the same audit: kernel_pin_key used an
    absolute path, so a pin written on one machine was permanently
    unusable after unpacking the project anywhere else."""

    def test_pin_key_is_relative_not_absolute(self):
        from llmos_toolkit.core.security import kernel_pin_key
        from llmos_toolkit.core.paths import PROJECT_ROOT
        real_kernel = PROJECT_ROOT / "kernel" / "HCF_LLMOS_Kernel_v1.3.6-C.md"
        if real_kernel.exists():
            key = kernel_pin_key(real_kernel)
            self.assertFalse(key.startswith("/"), f"key should be project-relative, got: {key}")
            self.assertEqual(key, "kernel/HCF_LLMOS_Kernel_v1.3.6-C.md")

    def test_pin_key_stable_across_different_absolute_locations(self):
        """The actual portability property: the same relative file, at
        two different absolute unpack locations, must get the same key."""
        from llmos_toolkit.core.security import kernel_pin_key
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            for root in (d1, d2):
                (Path(root) / "kernel").mkdir()
                (Path(root) / "kernel" / "test.md").write_text("content")
            with patch("llmos_toolkit.core.paths.PROJECT_ROOT", Path(d1)):
                key1 = kernel_pin_key(Path(d1) / "kernel" / "test.md")
            with patch("llmos_toolkit.core.paths.PROJECT_ROOT", Path(d2)):
                key2 = kernel_pin_key(Path(d2) / "kernel" / "test.md")
            self.assertEqual(key1, key2, "same relative file at different absolute roots must get the same key")


if __name__ == "__main__":
    unittest.main()
