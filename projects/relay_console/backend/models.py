# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Provider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"


class RelayMode(str, Enum):
    SYNC_AUTO = "sync_auto"        # API-to-API, no human approval per turn
    SYNC_GATED = "sync_gated"      # API-to-API, human PASS/EDIT/REJECT each turn
    ASYNC_GATED = "async_gated"    # no API automation -- human manually relays
                                     # between each provider's own actual UI;
                                     # this tool only tracks/logs the exchange


class GateAction(str, Enum):
    PASS = "pass"
    EDIT = "edit"
    REJECT = "reject"


class Participant(BaseModel):
    slot: str  # "A", "B", "C"
    provider: Provider
    model: str  # e.g. "claude-sonnet-5", "gpt-4o", "gemini-2.0-flash"
    label: Optional[str] = None  # display name, defaults to provider+slot


class Turn(BaseModel):
    turn_number: int
    from_slot: str
    to_slot: str
    content: str
    status: str = "pending"  # pending | approved | edited | rejected | sent | complete
    original_content: Optional[str] = None  # set only if edited, preserves what was proposed
    evidence_tier: Optional[str] = None  # V | I | A | U -- kernel A3 tiers, if the human/model tagging this turn supplies one
    provenance_note: Optional[str] = None  # free text: what this turn's content is actually grounded in, if known


class SessionConfig(BaseModel):
    mode: RelayMode
    participants: list[Participant] = Field(min_length=2, max_length=3)
    human_gate: bool = True  # ignored (forced True) for SYNC_GATED and ASYNC_GATED
    privacy_mode: bool = True  # no disk persistence unless explicit export
    opening_message: str
    starting_slot: str = "A"
    max_turns: Optional[int] = None  # None = run until human stops (gated modes only)


class SessionState(BaseModel):
    session_id: str
    config: SessionConfig
    turns: list[Turn] = []
    current_turn: int = 0
    status: str = "idle"  # idle | running | paused | stopped | complete
