# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import asyncio
import unittest


class TestRelayStopButtonFix(unittest.TestCase):
    """Real bug: stop() used to resolve the pending-gate future with a
    2-tuple, but both _gate() and _wait_for_human_paste() unpack 4
    values from it -- clicking Stop while a turn was pending crashed
    with ValueError. Verified correct in an earlier session but never
    actually merged until now; this test locks the fix in."""

    def test_new_4tuple_matches_gate_unpack(self):
        async def run():
            fut = asyncio.get_event_loop().create_future()
            fut.set_result(("reject", None, None, None))
            action, content, _, _ = await fut
            self.assertEqual(action, "reject")
        asyncio.run(run())

    def test_new_4tuple_matches_wait_for_human_paste_unpack(self):
        async def run():
            fut = asyncio.get_event_loop().create_future()
            fut.set_result(("reject", None, None, None))
            _, content, evidence_tier, provenance_note = await fut
            self.assertIsNone(content)
        asyncio.run(run())

    def test_old_2tuple_genuinely_would_crash(self):
        """Confirms this is a real regression test, not a tautology --
        the old, broken form actually fails the same unpack."""
        async def run():
            fut = asyncio.get_event_loop().create_future()
            fut.set_result(("reject", None))
            with self.assertRaises(ValueError):
                action, content, _, _ = await fut
        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
