"""
################################################################################
README
################################################################################

# AI-Powered Web App Emulator (Raspberry Pi / Ollama)

## Overview
This application creates a dynamic web interface driven by a local Ollama LLM.
The user types a natural language query; the LLM responds with a JSON UI
description; a Python renderer converts that JSON into HTML; and a lightweight
Flask server pushes the result to the browser in real-time via Server-Sent Events.

## Architecture
    User → Flask Web UI → Ollama LLM → JSON UI → HTML Renderer → Browser

## Prerequisites
- Python 3.9+
- Ollama running locally (https://ollama.com)
  - Pull a model, e.g.: `ollama pull gemma3:4b`
- Install Python dependencies:
    pip install flask requests

## Usage
    python main.py

Then open http://localhost:5000 in a browser (or the Pi's IP on the LAN).

## Supported JSON UI Components
    card, progress, table, dashboard, list, button, text, gauge, alert, form

## File Structure
    main.py          — this script (everything in one file)
    Logs/            — auto-created; contains log-YYYY-MM-DD.log files

## Configuration
Edit the CONFIG dict near the top of main.py to change:
    OLLAMA_URL, MODEL_NAME, HOST, PORT, LOG_DIR

## Notes
- The LLM is prompted to return ONLY valid JSON; any non-JSON fragments are
  stripped before parsing.
- Streaming is handled via SSE so the UI updates token-by-token.
- All errors are caught and shown as friendly alert cards in the browser.

################################################################################
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import json
import logging
import os
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, Response, render_template_string, request, stream_with_context

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CONFIG = {
    "OLLAMA_URL": "http://localhost:11434/api/generate",
    # "OLLAMA_URL": "http://localhost:11434",
    # "OLLAMA_URL": "http://localhost:11434/api/chat",
    # "OLLAMA_URL": "http://10.62.46.108:11434/api/chat",
    # "MODEL_NAME": "gemma3:4b",   # change to any model you have pulled
    # MODEL_NAME = "llama3.2:1b"                   # model name pulled in Ollama
    "MODEL_NAME": "llama3.2",                   # model name pulled in Ollama
    # MODEL_NAME = "llama2-uncensored:7b"                   # model name pulled in Ollama
    "HOST": "0.0.0.0",
    "PORT": 5000,
    "LOG_DIR": "Logs",
    "REQUEST_TIMEOUT": 120,      # seconds to wait for Ollama
}

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
def SetupLogging() -> logging.Logger:
    """Configure file + console logging; returns the root logger."""
    logDir = Path(CONFIG["LOG_DIR"])
    logDir.mkdir(parents=True, exist_ok=True)

    logFile = logDir / f"log-{datetime.now().strftime('%Y-%m-%d')}.log"

    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)

    # File handler – DEBUG and above
    fileHandler = logging.FileHandler(logFile, encoding="utf-8")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )

    # Console handler – INFO and above
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(
        logging.Formatter("[%(levelname)s] %(message)s")
    )

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    return logger


logger = SetupLogging()

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)

# ---------------------------------------------------------------------------
# System prompt for the LLM
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a UI generator. Given a user request, respond ONLY with a single valid JSON object describing the interface.

Supported component types and their schemas:

card:       {"type":"card","title":"...","value":"..."}
progress:   {"type":"progress","label":"...","value":0-100}
gauge:      {"type":"gauge","label":"...","value":0-100}
table:      {"type":"table","headers":["..."],"rows":[["..."]]}
list:       {"type":"list","title":"...","items":["..."]}
button:     {"type":"button","text":"...","action":"..."}
text:       {"type":"text","content":"..."}
alert:      {"type":"alert","level":"info|warning|error|success","message":"..."}
form:       {"type":"form","title":"...","fields":[{"label":"...","placeholder":"..."}]}
dashboard:  {"type":"dashboard","title":"...","children":[...any of the above...]}

Rules:
- Return ONLY the JSON object — no markdown, no explanation, no code fences.
- Use "dashboard" as the root type when multiple components are needed.
- Keep values realistic and relevant to the user's request.
"""

# ---------------------------------------------------------------------------
# HTML Renderer  (JSON → HTML string)
# ---------------------------------------------------------------------------

def RenderNode(node: dict) -> str:
    """Dispatch a JSON UI node to the correct renderer. Returns HTML string."""
    if not isinstance(node, dict):
        return '<div class="alert alert-error">Invalid node</div>'

    nodeType = node.get("type", "text")
    renderers = {
        "card":      RenderCard,
        "progress":  RenderProgress,
        "gauge":     RenderGauge,
        "table":     RenderTable,
        "list":      RenderList,
        "button":    RenderButton,
        "text":      RenderText,
        "alert":     RenderAlert,
        "form":      RenderForm,
        "dashboard": RenderDashboard,
    }
    renderFn = renderers.get(nodeType, RenderText)
    try:
        return renderFn(node)
    except Exception as exc:
        logger.error("Render error for type '%s': %s", nodeType, exc)
        return RenderAlert({"type": "alert", "level": "error",
                            "message": f"Render error: {exc}"})


def RenderCard(node: dict) -> str:
    """Render a simple metric card."""
    title = node.get("title", "")
    value = node.get("value", "")
    subtitle = node.get("subtitle", "")
    subtitleHtml = f'<p class="card-subtitle">{subtitle}</p>' if subtitle else ""
    return f"""
<div class="card">
  <h3 class="card-title">{title}</h3>
  <div class="card-value">{value}</div>
  {subtitleHtml}
</div>"""


def RenderProgress(node: dict) -> str:
    """Render a labelled progress bar (0-100)."""
    label = node.get("label", "")
    value = int(node.get("value", 0))
    value = max(0, min(100, value))
    return f"""
<div class="progress-wrap">
  <div class="progress-header">
    <span>{label}</span><span>{value}%</span>
  </div>
  <div class="progress-track">
    <div class="progress-fill" style="width:{value}%"></div>
  </div>
</div>"""


def RenderGauge(node: dict) -> str:
    """Render a circular SVG gauge."""
    label = node.get("label", "")
    value = int(node.get("value", 0))
    value = max(0, min(100, value))

    # SVG arc math
    radius = 54
    circumference = 2 * 3.14159 * radius
    offset = circumference * (1 - value / 100)

    # Colour by value
    if value >= 80:
        colour = "#ef4444"
    elif value >= 60:
        colour = "#f59e0b"
    else:
        colour = "#22c55e"

    return f"""
<div class="gauge-wrap">
  <svg viewBox="0 0 120 120" class="gauge-svg">
    <circle cx="60" cy="60" r="{radius}" fill="none" stroke="var(--track)" stroke-width="10"/>
    <circle cx="60" cy="60" r="{radius}" fill="none" stroke="{colour}" stroke-width="10"
            stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}"
            stroke-linecap="round" transform="rotate(-90 60 60)"/>
    <text x="60" y="60" dominant-baseline="middle" text-anchor="middle"
          class="gauge-val">{value}%</text>
    <text x="60" y="78" dominant-baseline="middle" text-anchor="middle"
          class="gauge-lbl">{label}</text>
  </svg>
</div>"""


def RenderTable(node: dict) -> str:
    """Render an HTML table from headers + rows."""
    headers = node.get("headers", [])
    rows    = node.get("rows", [])
    headerHtml = "".join(f"<th>{h}</th>" for h in headers)
    rowsHtml = ""
    for row in rows:
        cells = "".join(f"<td>{c}</td>" for c in row)
        rowsHtml += f"<tr>{cells}</tr>"
    return f"""
<div class="table-wrap">
  <table>
    <thead><tr>{headerHtml}</tr></thead>
    <tbody>{rowsHtml}</tbody>
  </table>
</div>"""


def RenderList(node: dict) -> str:
    """Render a styled unordered list."""
    title = node.get("title", "")
    items = node.get("items", [])
    titleHtml = f"<h3 class='list-title'>{title}</h3>" if title else ""
    itemsHtml = "".join(f"<li>{i}</li>" for i in items)
    return f"""
<div class="list-wrap">
  {titleHtml}
  <ul>{itemsHtml}</ul>
</div>"""


def RenderButton(node: dict) -> str:
    """Render a clickable button (action is display-only in this emulator)."""
    text   = node.get("text", "Click")
    action = node.get("action", "")
    return f'<button class="btn" title="{action}">{text}</button>'


def RenderText(node: dict) -> str:
    """Render a plain text/paragraph block."""
    content = node.get("content", str(node))
    return f'<p class="text-block">{content}</p>'


def RenderAlert(node: dict) -> str:
    """Render a coloured alert banner."""
    level   = node.get("level", "info")
    message = node.get("message", "")
    icons   = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "success": "✅"}
    icon    = icons.get(level, "ℹ️")
    return f'<div class="alert alert-{level}">{icon} {message}</div>'


def RenderForm(node: dict) -> str:
    """Render a simple display-only form (input fields are decorative here)."""
    title  = node.get("title", "Form")
    fields = node.get("fields", [])
    fieldsHtml = ""
    for field in fields:
        label       = field.get("label", "")
        placeholder = field.get("placeholder", "")
        fieldsHtml += f"""
<div class="form-field">
  <label>{label}</label>
  <input type="text" placeholder="{placeholder}" disabled/>
</div>"""
    return f"""
<div class="form-wrap">
  <h3 class="form-title">{title}</h3>
  {fieldsHtml}
</div>"""


def RenderDashboard(node: dict) -> str:
    """Render a grid dashboard containing child components."""
    title    = node.get("title", "")
    children = node.get("children", node.get("widgets", []))
    titleHtml    = f"<h2 class='dash-title'>{title}</h2>" if title else ""
    childrenHtml = "".join(RenderNode(child) for child in children)
    return f"""
<div class="dashboard">
  {titleHtml}
  <div class="dash-grid">
    {childrenHtml}
  </div>
</div>"""


# ---------------------------------------------------------------------------
# JSON extraction helper
# ---------------------------------------------------------------------------

def ExtractJson(rawText: str) -> dict:
    """
    Extract and parse the first JSON object found in rawText.
    Strips markdown code fences and leading/trailing prose.
    """
    # Remove markdown fences
    text = re.sub(r"```(?:json)?", "", rawText).strip()

    # Find the outermost {...}
    start = text.find("{")
    end   = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in LLM response")

    jsonStr = text[start : end + 1]
    return json.loads(jsonStr)


# ---------------------------------------------------------------------------
# Ollama streaming call
# ---------------------------------------------------------------------------

def StreamOllama(userQuery: str):
    """
    Generator: yields Server-Sent Event strings while streaming from Ollama.
    Sends token-by-token text events, then a final 'done' event with HTML.
    """
    prompt = f"{SYSTEM_PROMPT}\n\nUser request: {userQuery}"
    payload = {
        "model":  CONFIG["MODEL_NAME"],
        "prompt": prompt,
        "stream": True,
    }

    logger.info("Sending query to Ollama: %s", userQuery[:120])
    accumulated = ""

    try:
        # print(f"url: {CONFIG["OLLAMA_URL"]}")
        print("==url==")
        print(f"url: |{CONFIG['OLLAMA_URL']}|")
        print(f"payload: |{payload}|")
        print("==url==")
        
        with requests.post(
            CONFIG["OLLAMA_URL"],
            json=payload,
            stream=True,
            timeout=CONFIG["REQUEST_TIMEOUT"],
        ) as response:
            response.raise_for_status()

            for rawLine in response.iter_lines():
                if not rawLine:
                    continue
                try:
                    chunk = json.loads(rawLine)
                except json.JSONDecodeError:
                    continue

                token = chunk.get("response", "")
                accumulated += token

                # Stream each token to the browser so it can show a typing indicator
                tokenData = json.dumps({"type": "token", "text": token})
                yield f"data: {tokenData}\n\n"

                if chunk.get("done", False):
                    break

    except requests.exceptions.ConnectionError:
        errMsg = "Cannot connect to Ollama. Is it running? (ollama serve)"
        logger.error(errMsg)
        errJson = json.dumps({"type": "alert", "level": "error", "message": errMsg})
        htmlOut = RenderNode(json.loads(errJson))
        yield f"data: {json.dumps({'type':'done','html':htmlOut})}\n\n"
        return

    except requests.exceptions.Timeout:
        errMsg = "Ollama request timed out. Try a smaller model or increase REQUEST_TIMEOUT."
        logger.error(errMsg)
        errNode = {"type": "alert", "level": "error", "message": errMsg}
        yield f"data: {json.dumps({'type':'done','html':RenderNode(errNode)})}\n\n"
        return

    except Exception as exc:
        logger.error("Unexpected streaming error: %s\n%s", exc, traceback.format_exc())
        errNode = {"type": "alert", "level": "error",
                   "message": f"Streaming error: {exc}"}
        yield f"data: {json.dumps({'type':'done','html':RenderNode(errNode)})}\n\n"
        return

    # --- Parse JSON and render HTML ---
    logger.debug("Raw LLM output:\n%s", accumulated)
    try:
        uiJson  = ExtractJson(accumulated)
        htmlOut = RenderNode(uiJson)
        logger.info("Rendered component type: %s", uiJson.get("type", "unknown"))
    except (ValueError, json.JSONDecodeError, KeyError) as exc:
        logger.warning("JSON parse failed: %s — falling back to text node", exc)
        htmlOut = RenderNode({"type": "text", "content": accumulated.strip()})

    yield f"data: {json.dumps({'type':'done','html':htmlOut})}\n\n"


# ---------------------------------------------------------------------------
# Main HTML page (inline template)
# ---------------------------------------------------------------------------

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AI Web Emulator</title>
<style>
/* ── Variables ─────────────────────────────────────────────── */
:root {
  --bg:      #0d0f14;
  --surface: #161a23;
  --border:  #252b38;
  --accent:  #6ee7b7;
  --accent2: #818cf8;
  --text:    #e2e8f0;
  --muted:   #64748b;
  --track:   #1e293b;
  --radius:  12px;
  --font:    'JetBrains Mono', 'Fira Mono', 'Cascadia Code', monospace;
}

/* ── Reset ─────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { height: 100%; }

body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ── Header ────────────────────────────────────────────────── */
header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: .75rem;
  background: var(--surface);
}
header .logo {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: -.02em;
}
header .sub { color: var(--muted); font-size: .75rem; }

/* ── Input bar ─────────────────────────────────────────────── */
.input-bar {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  gap: .5rem;
  background: var(--surface);
}
.input-bar input {
  flex: 1;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  font-family: var(--font);
  font-size: .85rem;
  padding: .6rem 1rem;
  outline: none;
  transition: border-color .2s;
}
.input-bar input:focus { border-color: var(--accent); }
.input-bar button {
  background: var(--accent);
  color: var(--bg);
  border: none;
  border-radius: var(--radius);
  padding: .6rem 1.4rem;
  font-family: var(--font);
  font-size: .85rem;
  font-weight: 700;
  cursor: pointer;
  transition: opacity .2s;
}
.input-bar button:hover { opacity: .85; }
.input-bar button:disabled { opacity: .4; cursor: not-allowed; }

/* ── Status bar ────────────────────────────────────────────── */
#status {
  font-size: .72rem;
  color: var(--muted);
  padding: .3rem 1.5rem;
  border-bottom: 1px solid var(--border);
  min-height: 1.6rem;
  background: var(--bg);
}
#status.thinking { color: var(--accent); }

/* ── Render area ───────────────────────────────────────────── */
#render-area {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
}

/* ── Components ────────────────────────────────────────────── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.2rem 1.4rem;
  display: inline-block;
  min-width: 160px;
  margin: .4rem;
  transition: border-color .2s;
}
.card:hover { border-color: var(--accent2); }
.card-title  { font-size: .78rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; margin-bottom: .4rem; }
.card-value  { font-size: 2rem; font-weight: 700; color: var(--accent); }
.card-subtitle { font-size: .75rem; color: var(--muted); margin-top: .3rem; }

.progress-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 1.2rem;
  margin: .4rem 0;
}
.progress-header { display: flex; justify-content: space-between; font-size: .8rem; color: var(--muted); margin-bottom: .5rem; }
.progress-track  { background: var(--track); border-radius: 99px; height: 8px; overflow: hidden; }
.progress-fill   { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent2)); border-radius: 99px; transition: width .6s ease; }

.gauge-wrap { display: inline-block; width: 130px; margin: .4rem; }
.gauge-svg  { width: 100%; }
.gauge-val  { fill: var(--text); font-family: var(--font); font-size: 18px; font-weight: 700; }
.gauge-lbl  { fill: var(--muted); font-family: var(--font); font-size: 10px; }

.table-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  margin: .4rem 0;
}
table { width: 100%; border-collapse: collapse; font-size: .82rem; }
th    { background: var(--track); color: var(--accent); text-align: left; padding: .6rem .9rem; font-weight: 700; font-size: .72rem; text-transform: uppercase; letter-spacing: .05em; }
td    { padding: .55rem .9rem; border-top: 1px solid var(--border); }
tr:hover td { background: var(--track); }

.list-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 1.2rem;
  margin: .4rem 0;
}
.list-title { font-size: .85rem; color: var(--accent); margin-bottom: .5rem; }
ul { list-style: none; }
li { padding: .3rem 0; border-bottom: 1px solid var(--border); font-size: .82rem; }
li:last-child { border: none; }
li::before { content: "›"; color: var(--accent2); margin-right: .5rem; }

.btn {
  background: transparent;
  border: 1px solid var(--accent2);
  color: var(--accent2);
  border-radius: var(--radius);
  padding: .5rem 1.2rem;
  font-family: var(--font);
  font-size: .82rem;
  cursor: pointer;
  margin: .4rem;
  transition: background .2s, color .2s;
}
.btn:hover { background: var(--accent2); color: var(--bg); }

.text-block {
  background: var(--surface);
  border-left: 3px solid var(--accent2);
  padding: .8rem 1rem;
  border-radius: 0 var(--radius) var(--radius) 0;
  font-size: .85rem;
  line-height: 1.6;
  margin: .4rem 0;
}

.alert {
  padding: .75rem 1rem;
  border-radius: var(--radius);
  font-size: .82rem;
  margin: .4rem 0;
}
.alert-info    { background: #0e2a4a; border: 1px solid #1d4ed8; }
.alert-success { background: #052e16; border: 1px solid #16a34a; }
.alert-warning { background: #2d1900; border: 1px solid #d97706; }
.alert-error   { background: #2d0b0b; border: 1px solid #dc2626; }

.form-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.2rem;
  margin: .4rem 0;
  max-width: 420px;
}
.form-title { font-size: .9rem; color: var(--accent); margin-bottom: .8rem; }
.form-field { margin-bottom: .7rem; }
.form-field label { display: block; font-size: .75rem; color: var(--muted); margin-bottom: .25rem; }
.form-field input {
  width: 100%;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--muted);
  font-family: var(--font);
  font-size: .82rem;
  padding: .45rem .8rem;
}

.dashboard { width: 100%; }
.dash-title { font-size: 1rem; color: var(--accent); margin-bottom: 1rem; }
.dash-grid  { display: flex; flex-wrap: wrap; gap: .6rem; align-items: flex-start; }

/* ── Typing indicator ──────────────────────────────────────── */
.typing {
  display: inline-flex;
  gap: 4px;
  align-items: center;
  padding: .5rem 0;
}
.typing span {
  width: 6px; height: 6px;
  background: var(--accent);
  border-radius: 50%;
  animation: bounce .9s infinite;
}
.typing span:nth-child(2) { animation-delay: .15s; }
.typing span:nth-child(3) { animation-delay: .3s; }
@keyframes bounce {
  0%,80%,100% { transform: translateY(0); opacity: .4; }
  40%         { transform: translateY(-6px); opacity: 1; }
}

/* ── Fade-in for new content ───────────────────────────────── */
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
#render-area > * { animation: fadeIn .35s ease both; }
</style>
</head>
<body>

<header>
  <span class="logo">◈ AI Web Emulator</span>
  <span class="sub">powered by Ollama · JSON UI</span>
</header>

<div class="input-bar">
  <input id="queryInput" type="text"
         placeholder="e.g. Show a CPU/RAM/Disk dashboard"
         autocomplete="off"/>
  <button id="sendBtn" onclick="SendQuery()">Run ›</button>
</div>

<div id="status">Ready — type a query above and press Run.</div>

<div id="render-area">
  <div class="alert alert-info">
    ℹ️ Try: <em>"Create a system dashboard"</em> or <em>"Show a weekly tasks table"</em>
  </div>
</div>

<script>
const queryInput = document.getElementById('queryInput');
const sendBtn    = document.getElementById('sendBtn');
const status     = document.getElementById('status');
const renderArea = document.getElementById('render-area');

// Allow pressing Enter to submit
queryInput.addEventListener('keydown', e => { if (e.key === 'Enter') SendQuery(); });

function ShowTyping() {
  renderArea.innerHTML =
    '<div class="typing"><span></span><span></span><span></span></div>';
}

function SendQuery() {
  const query = queryInput.value.trim();
  if (!query) return;

  sendBtn.disabled = true;
  status.textContent = '⟳ Thinking…';
  status.className = 'thinking';
  ShowTyping();

  // Open SSE stream
  const evtSource = new EventSource(
    '/stream?q=' + encodeURIComponent(query)
  );

  let tokenBuffer = '';

  evtSource.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.type === 'token') {
      tokenBuffer += data.text;
      status.textContent = '⟳ Generating… ' + tokenBuffer.length + ' chars';
    }

    if (data.type === 'done') {
      evtSource.close();
      renderArea.innerHTML = data.html;
      status.textContent = '✓ Done';
      status.className   = '';
      sendBtn.disabled   = false;
    }
  };

  evtSource.onerror = function() {
    evtSource.close();
    renderArea.innerHTML =
      '<div class="alert alert-error">❌ Connection error. Check server logs.</div>';
    status.textContent = 'Error';
    status.className   = '';
    sendBtn.disabled   = false;
  };
}
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------

@app.route("/")
def Index():
    """Serve the main single-page interface."""
    return render_template_string(PAGE_TEMPLATE)


@app.route("/stream")
def Stream():
    """
    SSE endpoint.
    ?q=<user query>  → streams token events then a 'done' event with rendered HTML.
    """
    userQuery = request.args.get("q", "").strip()
    if not userQuery:
        def emptyGen():
            errNode = {"type": "alert", "level": "warning", "message": "No query provided."}
            yield f"data: {json.dumps({'type':'done','html':RenderNode(errNode)})}\n\n"
        return Response(stream_with_context(emptyGen()),
                        mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    return Response(
        stream_with_context(StreamOllama(userQuery)),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting AI Web Emulator on http://%s:%d", CONFIG["HOST"], CONFIG["PORT"])
    logger.info("Ollama endpoint : %s", CONFIG["OLLAMA_URL"])
    logger.info("Model           : %s", CONFIG["MODEL_NAME"])
    logger.info("Log directory   : %s/", CONFIG["LOG_DIR"])
    app.run(host=CONFIG["HOST"], port=CONFIG["PORT"], debug=False, threaded=True)
