# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Relay engine: causal-blocking turn sequencing across 2-3 participants.

SYNC_AUTO: engine calls each provider's API in round-robin order with
no pause for approval. Still emits state events over the WebSocket so
the browser can display it live -- "no human gate" doesn't mean "no
visibility," it means no PASS/EDIT/REJECT step blocks the turn.

SYNC_GATED: same round-robin API calls, but every proposed outgoing
message is held pending until the human sends PASS, EDIT (with new
content), or REJECT (turn discarded, same sender retries or session
pauses) over the WebSocket.

ASYNC_GATED: no provider calls at all. The human manually copies each
participant's output out of the relay console and pastes it into that
provider's own actual chat interface, then pastes the response back in.
This mode exists to give the current, already-familiar workflow (this
project's own human-relay pattern) a structured log and turn counter,
not to automate it.

Turn order for 3 participants defaults to round-robin (A -> B -> C ->
A -> ...). This is a design choice, not the only reasonable one --
star topology (all messages route through one hub participant) isn't
implemented here; round-robin was chosen because it matches how the
human relay has actually been operating this session.
"""
from __future__ import annotations

import asyncio
from typing import Callable, Optional

from .models import GateAction, Participant, RelayMode, SessionConfig, SessionState, Turn
from .providers import call_provider, ProviderError


class RelaySession:
    def __init__(self, session_id: str, config: SessionConfig, emit: Callable):
        self.state = SessionState(session_id=session_id, config=config)
        self.emit = emit  # async fn(event: dict) -> None, sends to WebSocket
        self._pending_gate: Optional[asyncio.Future] = None
        self._stop_requested = False

    def _slots(self) -> list[str]:
        return [p.slot for p in self.state.config.participants]

    def _next_slot(self, current: str) -> str:
        slots = self._slots()
        idx = slots.index(current)
        return slots[(idx + 1) % len(slots)]

    def _participant(self, slot: str) -> Participant:
        return next(p for p in self.state.config.participants if p.slot == slot)

    def _history_for(self, target_slot: str) -> list[dict]:
        """Builds the message history a given participant should see:
        every prior turn, with their own turns as 'assistant' and
        everyone else's as 'user' -- each participant experiences the
        relay as a normal back-and-forth conversation, not aware of the
        other slots by name unless that's in the opening message."""
        history = []
        for t in self.state.turns:
            if t.status not in ("approved", "sent", "complete"):
                continue
            role = "assistant" if t.from_slot == target_slot else "user"
            history.append({"role": role, "content": t.content})
        return history

    async def start(self):
        self.state.status = "running"
        await self.emit({"type": "session_started", "state": self.state.model_dump()})

        current_slot = self.state.config.starting_slot
        pending_content = self.state.config.opening_message

        while not self._stop_requested:
            if self.state.config.max_turns and self.state.current_turn >= self.state.config.max_turns:
                break

            next_slot = self._next_slot(current_slot)
            turn = Turn(
                turn_number=self.state.current_turn,
                from_slot=current_slot,
                to_slot=next_slot,
                content=pending_content,
                status="pending",
            )

            if self.state.config.mode != RelayMode.ASYNC_GATED:
                await self.emit({"type": "thinking", "slot": next_slot})

            if self.state.config.mode == RelayMode.ASYNC_GATED:
                # No API call. Wait for the human to paste in what the
                # target participant actually said, via their own real
                # chat interface.
                turn.status = "awaiting_human_paste"
                self.state.turns.append(turn)
                await self.emit({"type": "await_paste", "turn": turn.model_dump()})
                response_content, evidence_tier, provenance_note = await self._wait_for_human_paste(turn.turn_number)
                print(f"[TRACE] _wait_for_human_paste resumed with content={response_content!r}, "
                      f"evidence_tier={evidence_tier!r}, provenance_note={provenance_note!r}", flush=True)
            else:
                target = self._participant(next_slot)
                try:
                    history = self._history_for(next_slot) + [{"role": "user", "content": pending_content}]
                    if len(history) > 20:
                        # Real, unbounded-growth risk Jaidev's article flagged in a
                        # different form (fixed cost floor per call). Here the risk
                        # is different: history grows linearly with turn count, sent
                        # in full on every turn. Not auto-truncated -- silently
                        # cutting a relay's history risks breaking its coherence,
                        # a worse failure than visible growth. Logged so it's
                        # observable instead of silent.
                        print(f"[relay_console] WARNING: turn history for {next_slot} has "
                              f"grown to {len(history)} messages -- context size is unbounded "
                              "by design, this is expected to keep growing over a long session.")
                    try:
                        response_content = await asyncio.wait_for(
                            call_provider(target.provider, target.model, history),
                            timeout=90.0,
                        )
                    except asyncio.TimeoutError:
                        raise ProviderError(
                            f"{target.provider}/{target.model} did not respond within 90s -- "
                            "the relay stopped rather than hang indefinitely. This is the same "
                            "failure mode Jaidev's article described for an orchestrator router "
                            "with no fallback: one hung call was able to stall the whole workflow."
                        )
                    evidence_tier, provenance_note = None, None  # not supplied by direct API calls
                except ProviderError as e:
                    await self.emit({"type": "error", "detail": str(e)})
                    self.state.status = "stopped"
                    return

            reply_turn = Turn(
                turn_number=self.state.current_turn + 1,
                from_slot=next_slot,
                to_slot=self._next_slot(next_slot),
                content=response_content,
                status="pending",
                evidence_tier=evidence_tier,
                provenance_note=provenance_note,
            )
            print(f"[TRACE] reply_turn constructed successfully: turn_number={reply_turn.turn_number}, "
                  f"mode={self.state.config.mode}", flush=True)

            if self.state.config.mode == RelayMode.SYNC_GATED:
                # ASYNC_GATED doesn't gate again here -- the human already
                # approved this content by choosing what to paste in. A
                # second Pass/Edit/Reject step would just wait forever,
                # since the paste-bar UI never sends a gate_action message.
                approved_content = await self._gate(reply_turn)
                if approved_content is None:  # rejected, stop
                    self.state.status = "stopped"
                    await self.emit({"type": "session_stopped", "reason": "rejected"})
                    return
                reply_turn.content = approved_content
                reply_turn.status = "approved"
            else:
                reply_turn.status = "sent"

            self.state.turns.append(reply_turn)
            self.state.current_turn += 1
            await self.emit({"type": "turn_complete", "turn": reply_turn.model_dump()})

            current_slot = next_slot
            pending_content = reply_turn.content

        self.state.status = "complete"
        await self.emit({"type": "session_complete", "state": self.state.model_dump()})

    async def _gate(self, turn: Turn) -> Optional[str]:
        """Blocks until the human sends a gate action for this turn.
        Returns the approved content, or None if rejected."""
        self._pending_gate = asyncio.get_event_loop().create_future()
        await self.emit({"type": "gate_required", "turn": turn.model_dump()})
        action, content, _, _ = await self._pending_gate
        if action == GateAction.REJECT:
            return None
        if action == GateAction.EDIT:
            turn.original_content = turn.content
            return content
        return turn.content  # PASS

    async def _wait_for_human_paste(self, turn_number: int) -> tuple[str, Optional[str], Optional[str]]:
        self._pending_gate = asyncio.get_event_loop().create_future()
        _, content, evidence_tier, provenance_note = await self._pending_gate
        return content, evidence_tier, provenance_note

    def submit_gate_action(self, action: GateAction, content: Optional[str] = None):
        if self._pending_gate and not self._pending_gate.done():
            self._pending_gate.set_result((action, content, None, None))

    def submit_paste(self, content: str, evidence_tier: Optional[str] = None, provenance_note: Optional[str] = None):
        if self._pending_gate and not self._pending_gate.done():
            self._pending_gate.set_result((None, content, evidence_tier, provenance_note))

    def stop(self):
        self._stop_requested = True
        if self._pending_gate and not self._pending_gate.done():
            self._pending_gate.set_result((GateAction.REJECT, None))
