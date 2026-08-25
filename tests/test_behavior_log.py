# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Tests for behavior_log -- previously had no dedicated test file despite
every other feature this session getting one. Caught by external audit,
not self-discovered.
"""
from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class TestBehaviorLog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger_path = Path(self.tmp.name) / "growth_ledger.jsonl"
        # Real fix, 2026-08-22: this used to be return_value=self.ledger_path,
        # which routed EVERY get_state_path(...) call -- ledger, pending
        # observations, anything -- to the same single file regardless of
        # the filename argument. That silently merged two genuinely
        # separate files in production (growth_ledger.jsonl and
        # pending_observations.jsonl) into one, which specifically broke
        # any test exercising propose -> approve together: approve-pending
        # writes the ledger entry, then rewrites the (same, in the old
        # mock) pending file to remove the consumed entry -- a full
        # rewrite that silently wiped out the just-appended ledger entry
        # underneath it. Fixed to route by filename, matching real usage.
        def _fake_get_state_path(filename):
            return Path(self.tmp.name) / filename
        self.patcher = mock.patch(
            "llmos_toolkit.plugins.behavior_log.plugin.get_state_path",
            side_effect=_fake_get_state_path,
        )
        self.patcher.start()
        from llmos_toolkit.plugins.behavior_log import plugin
        self.plugin = plugin

    def tearDown(self):
        self.patcher.stop()
        self.tmp.cleanup()

    def _log(self, subject, category, severity, description, observer="unspecified", verified=False, source="", subject_version=""):
        args = argparse.Namespace(
            subject=subject, category=category, severity=severity, description=description,
            observer=observer, verified=verified, source=source, subject_version=subject_version,
        )
        return self.plugin.cmd_log_observation(args)

    def test_log_creates_entry_with_expected_fields(self):
        self._log("subj", "cat", "medium", "desc", observer="claude", verified=True, source="http://x")
        entries = self.plugin._load_observations()
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e["subject"], "subj")
        self.assertEqual(e["category"], "cat")
        self.assertEqual(e["severity"], "medium")
        self.assertTrue(e["verified_against_transcript"])
        self.assertEqual(e["source_cited"], "http://x")

    def test_source_defaults_to_none_not_empty_string(self):
        self._log("subj", "cat", "low", "desc")
        entries = self.plugin._load_observations()
        self.assertIsNone(entries[0]["source_cited"])

    def test_summary_reports_verified_vs_unverified_split(self):
        self._log("s1", "c1", "high", "d1", verified=True)
        self._log("s2", "c1", "high", "d2", verified=False)
        args = argparse.Namespace()
        # capture stdout
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(args)
        out = buf.getvalue()
        self.assertIn("1/2", out)

    def test_provenance_diversity_flags_shared_source_as_contamination(self):
        self._log("subj", "cat", "medium", "d1", observer="claude", source="http://same.example")
        self._log("subj", "cat", "medium", "d2", observer="gemini", source="http://same.example")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("likely shared contamination", out)

    def test_provenance_diversity_flags_distinct_sources_as_independent(self):
        self._log("subj", "cat", "medium", "d1", observer="claude", source="http://a.example")
        self._log("subj", "cat", "medium", "d2", observer="gemini", source="http://b.example")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("genuine independence signal", out)

    def test_non_observation_ledger_entries_are_ignored(self):
        # write a non-behavioral_observation entry directly -- must not be counted
        self.ledger_path.write_text(json.dumps({"event": "bug_fix", "label": "unrelated"}) + "\n")
        self._log("subj", "cat", "low", "d1")
        entries = self.plugin._load_observations()
        self.assertEqual(len(entries), 1, "only the behavioral_observation entry should be loaded, not the bug_fix one")

    def test_empty_ledger_summary_does_not_crash(self):
        args = argparse.Namespace()
        rc = self.plugin.cmd_summary(args)
        self.assertEqual(rc, 0)


    def test_record_outcome_links_to_existing_observation(self):
        self._log("subj", "cat", "medium", "desc")
        obs_id = self.plugin._load_observations()[0]["observation_id"]
        args = argparse.Namespace(observation_id=obs_id, outcome="confirmed", description="checked, held up", verified=True, amend=False)
        rc = self.plugin.cmd_record_outcome(args)
        self.assertEqual(rc, 0)
        outcomes = self.plugin._load_outcomes()
        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes[0]["observation_id"], obs_id)
        self.assertEqual(outcomes[0]["outcome"], "confirmed")

    def test_record_outcome_rejects_unknown_id(self):
        args = argparse.Namespace(observation_id="nonexistent", outcome="confirmed", description="x", verified=False, amend=False)
        rc = self.plugin.cmd_record_outcome(args)
        self.assertEqual(rc, 1, "an outcome for an id that was never logged must be rejected, not silently written")
        self.assertEqual(len(self.plugin._load_outcomes()), 0)

    def test_summary_calculates_calibration_rate_once_outcomes_exist(self):
        self._log("subj", "cat", "medium", "desc", observer="claude")
        obs_id = self.plugin._load_observations()[0]["observation_id"]
        args = argparse.Namespace(observation_id=obs_id, outcome="confirmed", description="held up", verified=True, amend=False)
        self.plugin.cmd_record_outcome(args)
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("confirmed rate: 1/1", out)

    def test_duplicate_outcome_rejected_without_amend(self):
        self._log("subj", "cat", "medium", "desc")
        obs_id = self.plugin._load_observations()[0]["observation_id"]
        first = argparse.Namespace(observation_id=obs_id, outcome="confirmed", description="d1", verified=True, amend=False)
        second = argparse.Namespace(observation_id=obs_id, outcome="disconfirmed", description="d2", verified=True, amend=False)
        rc1 = self.plugin.cmd_record_outcome(first)
        rc2 = self.plugin.cmd_record_outcome(second)
        self.assertEqual(rc1, 0)
        self.assertEqual(rc2, 1, "a second outcome for the same observation must be rejected without --amend")
        self.assertEqual(len(self.plugin._load_outcomes()), 1)

    def test_amend_allows_correction_and_calibration_uses_only_latest(self):
        self._log("subj", "cat", "medium", "desc", observer="claude")
        obs_id = self.plugin._load_observations()[0]["observation_id"]
        first = argparse.Namespace(observation_id=obs_id, outcome="confirmed", description="wrong initial read", verified=True, amend=False)
        amended = argparse.Namespace(observation_id=obs_id, outcome="disconfirmed", description="corrected after closer check", verified=True, amend=True)
        self.plugin.cmd_record_outcome(first)
        rc = self.plugin.cmd_record_outcome(amended)
        self.assertEqual(rc, 0, "--amend must allow a second outcome for the same id")
        self.assertEqual(len(self.plugin._load_outcomes()), 2, "both entries exist in the ledger (append-only)")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(argparse.Namespace())
        out = buf.getvalue()
        # only the LATEST (disconfirmed) outcome should count -- must not show confirmed rate 1/1
        self.assertNotIn("confirmed rate: 1/1", out, "amended outcome must replace the original for calibration, not add to it")

    def test_calibration_separates_verified_from_asserted_only(self):
        self._log("s1", "c1", "medium", "d1", observer="claude")
        self._log("s2", "c1", "medium", "d2", observer="gemini")
        id1 = [o for o in self.plugin._load_observations() if o["subject"] == "s1"][0]["observation_id"]
        id2 = [o for o in self.plugin._load_observations() if o["subject"] == "s2"][0]["observation_id"]
        self.plugin.cmd_record_outcome(argparse.Namespace(observation_id=id1, outcome="confirmed", description="checked for real", verified=True, amend=False))
        self.plugin.cmd_record_outcome(argparse.Namespace(observation_id=id2, outcome="confirmed", description="just asserted", verified=False, amend=False))
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("1 independently verified, 1 asserted only", out)

    def test_version_drift_no_data_is_honest_not_fabricated(self):
        self._log("subj", "cat", "low", "desc")  # no subject_version given
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_version_drift_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("nothing to compare across versions", out)

    def test_version_drift_single_version_reports_nothing_to_compare(self):
        self._log("subj", "cat", "low", "desc", subject_version="claude-sonnet-5")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_version_drift_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("no cross-version comparison possible yet", out)

    def test_version_drift_two_versions_produces_real_comparison(self):
        self._log("subj1", "shared-cat", "high", "old behavior", subject_version="claude-sonnet-4")
        self._log("subj2", "shared-cat", "low", "new behavior", subject_version="claude-sonnet-5")
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.plugin.cmd_version_drift_summary(argparse.Namespace())
        out = buf.getvalue()
        self.assertIn("real cross-version signal", out)
        self.assertIn("claude-sonnet-4", out)
        self.assertIn("claude-sonnet-5", out)

    def _propose(self, instance, subject, category, severity, description, verified=False, source="", experiment_id=""):
        args = argparse.Namespace(
            instance=instance, subject=subject, category=category, severity=severity,
            description=description, verified=verified, source=source, experiment_id=experiment_id,
        )
        return self.plugin.cmd_propose_observation(args)

    def test_approval_does_not_fabricate_verification(self):
        """Real regression test for a real bug: caught by an independent
        ChatGPT security audit, verified directly against the source
        before fixing. approve-pending used to hardcode
        verified_against_transcript=True unconditionally, conflating
        "a human approved this" with "a human verified this against a
        transcript" -- two different, independently-important facts.
        A proposal that never claimed verification must not become a
        VERIFIED entry just because a human approved it existing."""
        self._propose("gemini-free-tier", "subj", "cat", "low", "unverified claim", verified=False)
        real_id = self.plugin._load_pending()[0]["proposal_id"]
        args = argparse.Namespace(proposal_id=real_id)
        self.plugin.cmd_approve_pending(args)
        entries = self.plugin._load_observations()
        self.assertEqual(len(entries), 1)
        self.assertFalse(entries[0]["verified_against_transcript"])
        self.assertTrue(entries[0]["approved_by_human"])

    def test_approval_preserves_real_proposer_verification_claim(self):
        """The other half of the same fix: when a proposer DOES claim
        --verified, that real signal must survive approval intact, not
        get overwritten in either direction."""
        self._propose("claude-verified-instance", "subj", "cat", "medium", "checked claim", verified=True)
        real_id = self.plugin._load_pending()[0]["proposal_id"]
        args = argparse.Namespace(proposal_id=real_id)
        self.plugin.cmd_approve_pending(args)
        entries = self.plugin._load_observations()
        self.assertTrue(entries[0]["verified_against_transcript"])
        self.assertTrue(entries[0]["approved_by_human"])

    def test_approve_by_id_does_not_use_stale_list_position(self):
        """Real regression test for finding #3 (independent ChatGPT
        security audit): approve/reject used to operate on list index,
        a genuine TOCTOU risk -- item [3] during review could become a
        different entry by the time it was acted on. Confirms lookup
        is now by immutable ID: the correct entry is found and acted
        on by its real ID regardless of position in the list."""
        self._propose("instance-a", "subj-a", "cat", "low", "first", verified=False)
        self._propose("instance-b", "subj-b", "cat", "low", "second", verified=False)
        pending = self.plugin._load_pending()
        # Deliberately approve the SECOND entry by its real ID, proving
        # the lookup isn't silently falling back to position 0 or any
        # other implicit ordering.
        second_id = pending[1]["proposal_id"]
        args = argparse.Namespace(proposal_id=second_id)
        self.plugin.cmd_approve_pending(args)
        remaining_pending = self.plugin._load_pending()
        self.assertEqual(len(remaining_pending), 1)
        self.assertEqual(remaining_pending[0]["proposed_by"], "instance-a")
        approved = self.plugin._load_observations()
        self.assertEqual(len(approved), 1)
        self.assertEqual(approved[0]["observer"], "instance-b")

    def test_approve_unknown_id_fails_clearly_not_silently(self):
        args = argparse.Namespace(proposal_id="nonexistent")
        result = self.plugin.cmd_approve_pending(args)
        self.assertEqual(result, 1)
        self.assertEqual(self.plugin._load_observations(), [])

    def test_ambiguous_id_prefix_refuses_rather_than_guessing(self):
        """A short prefix matching more than one real proposal must
        refuse and name the conflict, never silently act on either
        one -- the whole point of the immutable-ID fix is that an
        action either finds exactly the right entry or fails clearly."""
        pending_path = self.plugin.get_state_path(self.plugin.PENDING_OBSERVATIONS_FILE)
        entries = [
            {"proposal_id": "aaaa1111", "proposed_by": "t1", "subject": "s1", "category": "c1",
             "severity": "low", "description": "d1", "source": None, "experiment_id": None,
             "verified_by_proposer": False, "proposed_at": "2026-01-01T00:00:00+00:00"},
            {"proposal_id": "aaaa2222", "proposed_by": "t2", "subject": "s2", "category": "c2",
             "severity": "low", "description": "d2", "source": None, "experiment_id": None,
             "verified_by_proposer": False, "proposed_at": "2026-01-01T00:00:00+00:00"},
        ]
        with open(pending_path, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        args = argparse.Namespace(proposal_id="aaaa")
        result = self.plugin.cmd_approve_pending(args)
        self.assertEqual(result, 1)
        self.assertEqual(len(self.plugin._load_pending()), 2)  # neither was consumed
        self.assertEqual(self.plugin._load_observations(), [])

    def test_legacy_pending_entry_without_id_gets_migrated_not_broken(self):
        """Real regression test: entries staged before this fix have no
        proposal_id field. _load_pending must backfill one, persist it,
        and keep it stable across reads -- not crash, and not
        regenerate a new ID every time the file is read."""
        pending_path = self.plugin.get_state_path(self.plugin.PENDING_OBSERVATIONS_FILE)
        legacy_entry = {
            "proposed_by": "old-instance", "subject": "s", "category": "c", "severity": "low",
            "description": "pre-migration entry", "source": None, "experiment_id": None,
            "proposed_at": "2026-01-01T00:00:00+00:00",
        }
        with open(pending_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(legacy_entry) + "\n")
        first_read = self.plugin._load_pending()
        self.assertEqual(len(first_read), 1)
        self.assertIn("proposal_id", first_read[0])
        backfilled_id = first_read[0]["proposal_id"]
        second_read = self.plugin._load_pending()
        self.assertEqual(second_read[0]["proposal_id"], backfilled_id)

    def test_supersede_removes_from_pending_but_preserves_permanent_trace(self):
        """Real regression test for a real gap: reject-pending discarded
        with zero permanent trace anywhere. supersede-pending is the
        third path -- removed from pending, but with an honest,
        permanent record distinct from both approval (would overstate
        it as VERIFIED-tier) and rejection (would wrongly imply the
        original claim was false)."""
        self._propose("test-instance", "subj", "cat", "low", "overtaken claim", verified=False)
        real_id = self.plugin._load_pending()[0]["proposal_id"]
        args = argparse.Namespace(proposal_id=real_id, reason="Overtaken by stronger evidence", evidence_ref="ref-123")
        result = self.plugin.cmd_supersede_pending(args)
        self.assertEqual(result, 0)
        self.assertEqual(self.plugin._load_pending(), [])
        entries = [json.loads(l) for l in open(self.ledger_path) if l.strip()]
        superseded = [e for e in entries if e.get("event") == "pending_proposal_superseded"]
        self.assertEqual(len(superseded), 1)
        self.assertEqual(superseded[0]["original_proposed_by"], "test-instance")
        self.assertEqual(superseded[0]["reason"], "Overtaken by stronger evidence")
        self.assertEqual(superseded[0]["superseded_by_evidence_ref"], "ref-123")
        # Not present as a normal behavioral_observation -- confirms it
        # was never promoted to VERIFIED-tier status like approval would.
        self.assertEqual([e for e in entries if e.get("event") == "behavioral_observation"], [])

    def test_supersede_unknown_id_fails_clearly(self):
        args = argparse.Namespace(proposal_id="nonexistent", reason="n/a", evidence_ref="")
        result = self.plugin.cmd_supersede_pending(args)
        self.assertEqual(result, 1)

    def test_reject_preserves_permanent_trace(self):
        """Real regression test for a real gap: reject-pending
        previously discarded with zero permanent trace anywhere.
        Found by external audit after supersede-pending was fixed for
        a different case but this one was missed."""
        self._propose("bad-instance", "subj", "cat", "low", "genuinely wrong claim", verified=False)
        real_id = self.plugin._load_pending()[0]["proposal_id"]
        args = argparse.Namespace(proposal_id=real_id, reason="Confirmed false")
        result = self.plugin.cmd_reject_pending(args)
        self.assertEqual(result, 0)
        self.assertEqual(self.plugin._load_pending(), [])
        entries = [json.loads(l) for l in open(self.ledger_path) if l.strip()]
        rejected = [e for e in entries if e.get("event") == "pending_proposal_rejected"]
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["original_proposed_by"], "bad-instance")
        self.assertEqual(rejected[0]["reason"], "Confirmed false")
        self.assertEqual([e for e in entries if e.get("event") == "behavioral_observation"], [])

    def test_supersede_is_idempotent_under_simulated_crash_recovery(self):
        """Real regression test simulating the exact crash window an
        external audit identified: a real failure between the ledger
        append and the pending-file save could leave the proposal back
        in pending even though its supersession event already exists.
        A retry must not create a duplicate ledger event, and must
        still finish the pending cleanup."""
        self._propose("test-instance", "subj", "cat", "low", "overtaken claim", verified=False)
        real_id = self.plugin._load_pending()[0]["proposal_id"]
        args = argparse.Namespace(proposal_id=real_id, reason="First attempt", evidence_ref="ref-1")
        self.plugin.cmd_supersede_pending(args)
        # Simulate the crash: re-inject the same entry back into pending,
        # as if the ledger write succeeded but the pending save crashed.
        pending_path = self.plugin.get_state_path(self.plugin.PENDING_OBSERVATIONS_FILE)
        replay_entry = {
            "proposal_id": real_id, "proposed_by": "test-instance", "subject": "subj",
            "category": "cat", "severity": "low", "description": "overtaken claim",
            "source": None, "experiment_id": None, "verified_by_proposer": False,
            "proposed_at": "2026-01-01T00:00:00+00:00",
        }
        with open(pending_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(replay_entry) + "\n")
        self.assertEqual(len(self.plugin._load_pending()), 1)
        # Retry with different args -- if this weren't idempotent, it
        # would write a second, contradictory ledger event.
        retry_args = argparse.Namespace(proposal_id=real_id, reason="Retry after crash", evidence_ref="ref-2")
        self.plugin.cmd_supersede_pending(retry_args)
        entries = [json.loads(l) for l in open(self.ledger_path) if l.strip()]
        superseded = [e for e in entries if e.get("event") == "pending_proposal_superseded"
                      and e.get("original_proposal_id") == real_id]
        self.assertEqual(len(superseded), 1)
        self.assertEqual(superseded[0]["reason"], "First attempt")  # the original write, not the retry
        self.assertEqual(self.plugin._load_pending(), [])

    def test_decision_type_survives_direct_log(self):
        """Real regression test: decision_type field was defined in the
        ledger security spec section 7.5 but had no tooling support at
        all -- found by external audit. Confirms it's now real."""
        args = argparse.Namespace(
            subject="s", category="c", severity="low", description="d",
            observer="test", verified=False, source="", subject_version="",
            intervention_required=False, quirk_id="", decision_type="continuation_approval",
        )
        self.plugin.cmd_log_observation(args)
        entries = self.plugin._load_observations()
        self.assertEqual(entries[0]["decision_type"], "continuation_approval")

    def test_decision_type_survives_propose_then_approve(self):
        """The harder path: decision_type must survive the full
        pending -> approved lifecycle, not just direct logging."""
        args = argparse.Namespace(
            instance="test-instance", subject="s", category="c", severity="low",
            description="d", source="", experiment_id="", verified=False,
            decision_type="directive_change",
        )
        self.plugin.cmd_propose_observation(args)
        real_id = self.plugin._load_pending()[0]["proposal_id"]
        self.plugin.cmd_approve_pending(argparse.Namespace(proposal_id=real_id))
        entries = self.plugin._load_observations()
        self.assertEqual(entries[0]["decision_type"], "directive_change")

    def _simulate_crash_recreate_pending(self, real_id, proposed_by="test-instance"):
        """Real helper matching the external audit's own methodology:
        re-inject the same proposal into pending, exactly as if a crash
        happened after a terminal-transition ledger write succeeded but
        before the pending-file save completed."""
        pending_path = self.plugin.get_state_path(self.plugin.PENDING_OBSERVATIONS_FILE)
        replay_entry = {
            "proposal_id": real_id, "proposed_by": proposed_by, "subject": "subj",
            "category": "cat", "severity": "low", "description": "overtaken claim",
            "source": None, "experiment_id": None, "verified_by_proposer": False,
            "decision_type": None, "proposed_at": "2026-01-01T00:00:00+00:00",
        }
        with open(pending_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(replay_entry) + "\n")

    def test_approve_is_idempotent_under_simulated_crash_recovery(self):
        """Real regression test for the external audit's second pass:
        approve-pending's append-first ordering prevented loss but not
        duplication -- a genuine crash/retry produced two separate
        behavioral_observation entries with different observation_ids
        for one proposal. This also required adding original_proposal_id
        to the approved entry, which didn't exist before -- a real,
        independent gap idempotency depended on."""
        self._propose("test-instance", "subj", "cat", "low", "overtaken claim", verified=False)
        real_id = self.plugin._load_pending()[0]["proposal_id"]
        self.plugin.cmd_approve_pending(argparse.Namespace(proposal_id=real_id))
        self._simulate_crash_recreate_pending(real_id)
        self.assertEqual(len(self.plugin._load_pending()), 1)
        self.plugin.cmd_approve_pending(argparse.Namespace(proposal_id=real_id))
        entries = self.plugin._load_observations()
        matching = [e for e in entries if e.get("original_proposal_id") == real_id]
        self.assertEqual(len(matching), 1)
        self.assertEqual(self.plugin._load_pending(), [])

    def test_reject_is_idempotent_under_simulated_crash_recovery(self):
        """Same fix, applied to reject-pending: a crash/retry previously
        produced two rejection events with different reasons."""
        self._propose("test-instance", "subj", "cat", "low", "overtaken claim", verified=False)
        real_id = self.plugin._load_pending()[0]["proposal_id"]
        self.plugin.cmd_reject_pending(argparse.Namespace(proposal_id=real_id, reason="first reason"))
        self._simulate_crash_recreate_pending(real_id)
        self.plugin.cmd_reject_pending(argparse.Namespace(proposal_id=real_id, reason="second reason"))
        entries = [json.loads(l) for l in open(self.ledger_path) if l.strip()]
        matching = [e for e in entries if e.get("event") == "pending_proposal_rejected"
                    and e.get("original_proposal_id") == real_id]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["reason"], "first reason")
        self.assertEqual(self.plugin._load_pending(), [])

    def test_conflicting_terminal_transition_is_refused_not_silently_resolved(self):
        """Real regression test for the exact anomaly the audit named:
        a proposal ending up with two DIFFERENT terminal transitions
        (approved, then a crash-recovery retry attempts reject) must be
        refused as a conflict needing human review, never silently
        picked one way or the other."""
        self._propose("test-instance", "subj", "cat", "low", "claim", verified=False)
        real_id = self.plugin._load_pending()[0]["proposal_id"]
        self.plugin.cmd_approve_pending(argparse.Namespace(proposal_id=real_id))
        self._simulate_crash_recreate_pending(real_id)
        result = self.plugin.cmd_reject_pending(argparse.Namespace(proposal_id=real_id, reason="conflict attempt"))
        self.assertEqual(result, 1)
        entries = [json.loads(l) for l in open(self.ledger_path) if l.strip()]
        rejections = [e for e in entries if e.get("event") == "pending_proposal_rejected"
                      and e.get("original_proposal_id") == real_id]
        self.assertEqual(len(rejections), 0)
        # The pending entry deliberately stays -- the conflict is refused,
        # not cleaned up as if it were resolved.
        self.assertEqual(len(self.plugin._load_pending()), 1)


if __name__ == "__main__":
    unittest.main()
