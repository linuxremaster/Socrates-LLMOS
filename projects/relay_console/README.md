<!--
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
-->

# Relay Console

Browser control room for a 2-3 way LLM relay, per
`Asynchronous_synchronous_web_relay.md`'s design. Three modes, one
codebase, switched via the UI mode selector — not three separate apps.

## Status: built, NOT independently tested

This was written in a sandboxed environment with no network access, so
it could not be installed or run end-to-end here. What was actually
verified: all 4 backend Python files parse as syntactically valid
Python (`ast.parse`, confirmed). What was NOT verified: that it
actually runs, that the WebSocket protocol between frontend and
backend is bug-free in practice, or that any provider API call
succeeds. Treat this as a solid first draft to run and debug on your
own machine, not a tested release.

## The three modes

- **Synchronous — Auto** (`sync_auto`): the relay calls each configured
  provider's API in round-robin turn order automatically. No approval
  step. You still see it happen live in the browser.
- **Synchronous — Human Gate** (`sync_gated`): same API calls, but
  every outgoing message is held for you to **Pass / Send Edited /
  Reject** before it goes to the next participant.
- **Asynchronous — Human Relay** (`async_gated`): no API calls at all.
  You copy each participant's message out of the console and paste it
  into that provider's actual chat interface yourself, then paste
  their response back in. This is a structured log/turn-counter for
  the same manual relay workflow this project has been using all
  along — not an automation of it.

2 or 3 participants, any mix of Anthropic / OpenAI / Google, configured
per session in the setup panel.

## Running it

```
cd projects/relay_console
pip install -r requirements.txt
cp .env.example .env    # fill in keys for whichever providers you'll use
uvicorn backend.main:app --reload --port 8420
```

Open `http://localhost:8420`. `async_gated` mode needs no keys at all.

## Running on Termux (Android)

Works — this is a plain local web server, exactly what Termux is built
for. Native Android without Termux (a real packaged app) is a
different, much bigger project not attempted here.

```
pkg install python rust
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.main:app --reload --port 8420 --host 127.0.0.1
```

Then open the browser on the same device to `http://localhost:8420`.

**Why `rust` first:** `pydantic`'s core is Rust-based; Termux usually
has no prebuilt wheel for it, so pip compiles from source, which needs
the Rust toolchain present first. This step can take a while — that's
expected, not a hang.

**Why plain `uvicorn`, not `uvicorn[standard]`:** the `[standard]`
extras (`uvloop`, `httptools`) are C-extension performance add-ons that
are more likely to fail to build on Termux. Plain `uvicorn` runs fine
without them, just without that extra speed — not needed for a local
single-user relay.

**Background execution:** Android can suspend Termux when it's not the
foreground app, which would kill an in-progress relay session. Run
`termux-wake-lock` before starting a long `sync_auto`/`sync_gated`
session if you'll switch away from Termux mid-relay.

## Privacy

Privacy mode is on by default, per the design doc's own recommendation:
sessions live in server memory only. Nothing touches disk until you
click **Export Session**, which downloads the full transcript as JSON.
Restarting the server clears all in-memory sessions.

## TOS posture

Built to the "generally safe" architecture the design doc itself lays
out: official APIs only, credentials stay server-side, no scraping or
automating any provider's consumer web UI, human gate available and
defaulted toward in two of the three modes. This is not a legal
opinion — check each provider's current terms for your specific use
before running an extended automated (`sync_auto`) session.

## Architecture

```
browser (index.html/app.js)
    │  WebSocket (session state, gate actions)
    ▼
backend/main.py (FastAPI + WebSocket)
    │
    ▼
backend/relay_engine.py (turn sequencing, human gate, 3 modes)
    │
    ▼
backend/providers.py (Anthropic / OpenAI / Google SDK calls)
```

`models.py` defines the shared data shapes (`Participant`, `Turn`,
`SessionConfig`, `SessionState`) used across all three files.

## Known gaps, not yet built

- No persistence-on-crash — an in-progress session is gone if the
  server process dies before export.
- No auth on the WebSocket endpoint — fine for local single-user use,
  not fine if ever exposed beyond localhost.
- 3-way turn order is fixed round-robin (A→B→C→A). A star topology
  (all messages route through one hub participant) was considered and
  not implemented — round-robin matches how the manual human relay has
  actually been operating.
- Test coverage is real but partial: `tests/test_relay_stop_button_fix.py`
  and `tests/test_external_audit_20260820_fixes.py` cover the Stop-button
  crash, message duplication, and turn-numbering fixes -- but as logic
  simulations, not by importing and testing `RelaySession` directly,
  since `pydantic`/`fastapi` aren't installable in the dev sandbox
  these were written in (no external network access). Testing the real
  class directly, wherever those dependencies are actually available,
  would be strictly better coverage than what exists now.

**End Relay Console README**
