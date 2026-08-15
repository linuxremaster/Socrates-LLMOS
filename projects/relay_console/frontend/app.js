// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

const PROVIDER_MODELS = {
  anthropic: ["claude-sonnet-5", "claude-opus-4-8", "claude-haiku-4-5-20251001"],
  openai: ["gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"],
  google: ["gemini-3.6-flash", "gemini-3.1-pro", "gemini-3.5-flash-lite"],
};

const sessionId = crypto.randomUUID();
let ws = null;
let participants = [
  { slot: "A", provider: "anthropic", model: PROVIDER_MODELS.anthropic[0] },
  { slot: "B", provider: "openai", model: PROVIDER_MODELS.openai[0] },
];

const el = (id) => document.getElementById(id);

function renderParticipantConfig() {
  const container = el("participants-config");
  container.innerHTML = "";
  participants.forEach((p, i) => {
    const row = document.createElement("div");
    row.className = "participant-config-row";
    row.innerHTML = `
      <span class="slot-badge">${p.slot}</span>
      <select data-i="${i}" class="provider-select">
        ${Object.keys(PROVIDER_MODELS).map(k => `<option value="${k}" ${k === p.provider ? "selected" : ""}>${k}</option>`).join("")}
      </select>
      <select data-i="${i}" class="model-select">
        ${PROVIDER_MODELS[p.provider].map(m => `<option value="${m}" ${m === p.model ? "selected" : ""}>${m}</option>`).join("")}
      </select>
    `;
    container.appendChild(row);
  });
  container.querySelectorAll(".provider-select").forEach(sel => {
    sel.addEventListener("change", (e) => {
      const i = +e.target.dataset.i;
      participants[i].provider = e.target.value;
      participants[i].model = PROVIDER_MODELS[e.target.value][0];
      renderParticipantConfig();
    });
  });
  container.querySelectorAll(".model-select").forEach(sel => {
    sel.addEventListener("change", (e) => {
      participants[+e.target.dataset.i].model = e.target.value;
    });
  });
  el("add-participant").disabled = participants.length >= 3;
}

el("add-participant").addEventListener("click", () => {
  if (participants.length >= 3) return;
  const nextSlot = String.fromCharCode(65 + participants.length); // C
  participants.push({ slot: nextSlot, provider: "google", model: PROVIDER_MODELS.google[0] });
  renderParticipantConfig();
});

function renderParticipantRow() {
  const row = el("participant-row");
  row.innerHTML = participants.map(p => `
    <div class="participant-card" id="card-${p.slot}">
      <div class="participant-header">
        <span class="lamp" id="lamp-${p.slot}"></span>
        <span class="participant-label">${p.slot} — ${p.provider}</span>
      </div>
      <div class="participant-model">${p.model}</div>
    </div>
  `).join("");
}

function setLamp(slot, state) {
  const lamp = el(`lamp-${slot}`);
  if (!lamp) return;
  lamp.className = "lamp " + state;
}

function appendTranscript(turn) {
  const t = el("transcript");
  const div = document.createElement("div");
  div.className = "transcript-turn";
  div.innerHTML = `
    <div class="transcript-meta">TURN ${turn.turn_number} — ${turn.from_slot} → ${turn.to_slot} — ${turn.status.toUpperCase()}</div>
    <div class="transcript-content"></div>
  `;
  div.querySelector(".transcript-content").textContent = turn.content;
  t.appendChild(div);
  t.scrollTop = t.scrollHeight;
}

function setStatus(status) {
  const pill = el("session-status");
  pill.textContent = status.toUpperCase();
  pill.className = "status-pill " + (status === "running" ? "running" : status === "stopped" ? "stopped" : "idle");
}

let pendingTurn = null;

function handleEvent(evt) {
  switch (evt.type) {
    case "session_started":
      setStatus("running");
      break;
    case "thinking":
      setLamp(evt.slot, "thinking");
      break;
    case "turn_complete":
      setLamp(evt.turn.from_slot, "sent");
      el("turn-counter").textContent = `TURN ${evt.turn.turn_number}`;
      appendTranscript(evt.turn);
      break;
    case "gate_required":
      pendingTurn = evt.turn;
      setLamp(evt.turn.from_slot, "ready");
      el("gate-bar").hidden = false;
      el("gate-label").textContent = `${evt.turn.from_slot} → ${evt.turn.to_slot} — pending approval`;
      el("gate-content").value = evt.turn.content;
      break;
    case "await_paste":
      pendingTurn = evt.turn;
      el("paste-bar").hidden = false;
      appendTranscript(evt.turn);
      break;
    case "error":
      alert("Relay error: " + evt.detail);
      setStatus("stopped");
      break;
    case "session_stopped":
    case "session_complete":
      setStatus(evt.type === "session_complete" ? "idle" : "stopped");
      el("gate-bar").hidden = true;
      el("paste-bar").hidden = true;
      break;
  }
}

el("start-btn").addEventListener("click", () => {
  const mode = el("mode-select").value;
  const config = {
    mode,
    participants,
    human_gate: mode !== "sync_auto",
    privacy_mode: el("privacy-mode").checked,
    opening_message: el("opening-message").value,
    starting_slot: participants[0].slot,
  };

  el("setup-panel").hidden = true;
  el("console-panel").hidden = false;
  renderParticipantRow();

  ws = new WebSocket(`ws://${location.host}/ws/${sessionId}`);
  ws.onopen = () => ws.send(JSON.stringify({ action: "start_session", config }));
  ws.onmessage = (e) => handleEvent(JSON.parse(e.data));
});

el("gate-pass").addEventListener("click", () => {
  ws.send(JSON.stringify({ action: "gate_action", gate_action: "pass" }));
  el("gate-bar").hidden = true;
});
el("gate-edit").addEventListener("click", () => {
  ws.send(JSON.stringify({ action: "gate_action", gate_action: "edit", content: el("gate-content").value }));
  el("gate-bar").hidden = true;
});
el("gate-reject").addEventListener("click", () => {
  ws.send(JSON.stringify({ action: "gate_action", gate_action: "reject" }));
  el("gate-bar").hidden = true;
});

el("copy-pending-btn").addEventListener("click", async () => {
  if (!pendingTurn) return;
  try {
    await navigator.clipboard.writeText(pendingTurn.content);
    const btn = el("copy-pending-btn");
    const original = btn.textContent;
    btn.textContent = "Copied";
    setTimeout(() => { btn.textContent = original; }, 1200);
  } catch (e) {
    alert("Clipboard access failed -- select and copy the message text manually.");
  }
});

el("paste-submit").addEventListener("click", () => {
  ws.send(JSON.stringify({ action: "submit_paste", content: el("paste-content").value }));
  el("paste-content").value = "";
  el("paste-bar").hidden = true;
});

el("stop-btn").addEventListener("click", () => {
  ws.send(JSON.stringify({ action: "stop" }));
});

el("export-btn").addEventListener("click", async () => {
  const res = await fetch(`/api/export/${sessionId}`);
  const data = await res.json();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `relay_session_${sessionId}.json`;
  a.click();
});

renderParticipantConfig();
