# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Relay Console -- browser control room for a 2-3 way LLM relay.

Run with:
    uvicorn main:app --reload --port 8420

Then open http://localhost:8420 in a browser. Requires API keys set as
environment variables (or in a .env file, see .env.example) for
whichever providers you configure in a session -- SYNC_AUTO and
SYNC_GATED modes only. ASYNC_GATED mode needs no API keys at all.

Privacy mode is ON by default per this project's own design doc:
sessions live in memory only, nothing written to disk unless the human
explicitly exports.
"""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .models import GateAction, SessionConfig
from .relay_engine import RelaySession

load_dotenv()

app = FastAPI(title="Relay Console")

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# In-memory only -- privacy mode default. Sessions vanish when the
# process restarts unless a session is explicitly exported by the human.
SESSIONS: dict[str, RelaySession] = {}
BACKGROUND_TASKS: dict[str, asyncio.Task] = {}  # keeps a reference so the
# start()-running task isn't garbage-collected while still in flight


@app.get("/")
async def index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.post("/api/debug-log")
async def debug_log(request: Request):
    """Temporary diagnostic route: the browser can't show its own JS
    console output on this device without a desktop connection. This
    prints whatever the frontend reports straight to this terminal,
    so a client-side error becomes visible without needing devtools."""
    body = await request.json()
    print(f"[BROWSER JS ERROR] {body.get('message', '(no message)')}")
    print(f"  at {body.get('source', '?')}:{body.get('line', '?')}")
    if body.get("stack"):
        print(f"  stack: {body['stack']}")
    return {"logged": True}


@app.websocket("/ws/{session_id}")
async def relay_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()

    async def emit(event: dict):
        await websocket.send_json(event)

    try:
        while True:
            msg = await websocket.receive_json()
            action = msg.get("action")

            if action == "start_session":
                config = SessionConfig(**msg["config"])
                sid = session_id or str(uuid.uuid4())
                session = RelaySession(sid, config, emit)
                SESSIONS[sid] = session
                # NOT awaited here -- session.start() is the relay's whole
                # main loop, which blocks waiting for a human paste/gate
                # action. Awaiting it inline would freeze this same loop
                # before it could ever receive that later message -- a
                # real deadlock, confirmed live: submit_paste and stop both
                # sent successfully from the browser, neither ever reached
                # its handler, because this loop never got back to
                # websocket.receive_json() to pick them up. Scheduled as a
                # concurrent task instead; reference kept so it isn't
                # garbage-collected mid-flight.
                task = asyncio.create_task(session.start())
                BACKGROUND_TASKS[sid] = task

            elif action == "gate_action":
                session = SESSIONS.get(session_id)
                if session:
                    session.submit_gate_action(GateAction(msg["gate_action"]), msg.get("content"))

            elif action == "submit_paste":
                print(f"[TRACE] submit_paste received for session_id={session_id}, "
                      f"session found in SESSIONS: {session_id in SESSIONS}", flush=True)
                session = SESSIONS.get(session_id)
                if session:
                    session.submit_paste(
                        msg["content"],
                        evidence_tier=msg.get("evidence_tier"),
                        provenance_note=msg.get("provenance_note"),
                    )
                    print(f"[TRACE] submit_paste() called on session object successfully", flush=True)

            elif action == "stop":
                session = SESSIONS.get(session_id)
                if session:
                    session.stop()

    except WebSocketDisconnect:
        pass


@app.get("/api/export/{session_id}")
async def export_session(session_id: str):
    """Explicit export -- the only way session content leaves memory
    and touches disk, per privacy-mode-default design."""
    session = SESSIONS.get(session_id)
    if not session:
        return {"error": "session not found"}
    return session.state.model_dump()
