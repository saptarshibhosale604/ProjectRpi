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

## Streaming Strategy
The LLM streams JSON token-by-token. As tokens arrive:
  1. Each token is logged to the log file with a [TOKEN] prefix.
  2. The accumulator is scanned after every token for complete child objects.
     A child is "complete" when its brace depth returns to 1 (inside the root
     object) after opening above 1. Completed children are rendered immediately
     and pushed to the browser as "component" SSE events — no need to wait for
     the full response.
  3. A final "done" SSE event signals the browser to stop the typing indicator.

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
- The LLM is prompted to return ONLY valid JSON.
- All tokens are logged with [TOKEN] prefix for debugging.
- Components render as soon as they are complete in the stream.
- All errors surface as alert cards in the browser, never a crash.

################################################################################
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import json
import logging
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
    "OLLAMA_URL":      "http://localhost:11434/api/generate",
    # "MODEL_NAME":      "gemma3:4b",   # change to any model you have pulled
    # "MODEL_NAME": "llama3.2:1b",                   # model name pulled in Ollama
    "MODEL_NAME": "llama3.2",                   # model name pulled in Ollama
    # MODEL_NAME = "llama2-uncensored:7b"                   # model name pulled in Ollama
    "HOST":            "0.0.0.0",
    "PORT":            5000,
    "LOG_DIR":         "Logs",
    "REQUEST_TIMEOUT": 120,           # seconds to wait for Ollama
}

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
def SetupLogging() -> logging.Logger:
    """
    Configure file + console logging.
    File handler logs DEBUG and above (includes [TOKEN] lines).
    Console handler logs INFO and above only.
    Returns the named 'app' logger.
    """
    logDir = Path(CONFIG["LOG_DIR"])
    logDir.mkdir(parents=True, exist_ok=True)

    logFile = logDir / f"log-{datetime.now().strftime('%Y-%m-%d')}.log"

    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers on reload
    if logger.handlers:
        return logger

    # File handler – DEBUG and above (tokens go here)
    fileHandler = logging.FileHandler(logFile, encoding="utf-8")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )

    # Console handler – INFO and above (no token noise on screen)
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
# System prompt
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
    title    = node.get("title", "")
    value    = node.get("value", "")
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
    value = max(0, min(100, int(node.get("value", 0))))
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
    """Render a circular SVG gauge with colour coded by value."""
    label = node.get("label", "")
    value = max(0, min(100, int(node.get("value", 0))))
    radius        = 54
    circumference = 2 * 3.14159 * radius
    offset        = circumference * (1 - value / 100)
    colour = "#ef4444" if value >= 80 else ("#f59e0b" if value >= 60 else "#22c55e")
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
    headers    = node.get("headers", [])
    rows       = node.get("rows", [])
    headerHtml = "".join(f"<th>{h}</th>" for h in headers)
    rowsHtml   = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
        for row in rows
    )
    return f"""
<div class="table-wrap">
  <table>
    <thead><tr>{headerHtml}</tr></thead>
    <tbody>{rowsHtml}</tbody>
  </table>
</div>"""


def RenderList(node: dict) -> str:
    """Render a styled unordered list."""
    title     = node.get("title", "")
    items     = node.get("items", [])
    titleHtml = f"<h3 class='list-title'>{title}</h3>" if title else ""
    itemsHtml = "".join(f"<li>{i}</li>" for i in items)
    return f"""
<div class="list-wrap">
  {titleHtml}
  <ul>{itemsHtml}</ul>
</div>"""


def RenderButton(node: dict) -> str:
    """Render a display button (action is decorative in this emulator)."""
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
    """Render a display-only form."""
    title      = node.get("title", "Form")
    fields     = node.get("fields", [])
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
    """Render a grid dashboard — used for the final consolidated view."""
    title        = node.get("title", "")
    children     = node.get("children", node.get("widgets", []))
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
# Incremental JSON child extractor
# ---------------------------------------------------------------------------

def ExtractCompletedChildren(text: str, lastPos: int) -> tuple[list[dict], int]:
    """
    Scan `text` from `lastPos` looking for complete JSON child objects.

    Strategy:
      - The LLM wraps everything in a root object { ... }.
      - Children live inside arrays like "children": [ {...}, {...} ].
      - A child object is "complete" when we open a '{' at brace-depth >= 2
        (we are inside the root AND inside an array) and the depth returns
        to the level it was at before that '{'.
      - We also handle a non-dashboard root (single component) by treating
        the entire root object as one component once it closes.

    Returns:
        (list of parsed child dicts, new lastPos to resume from next call)
    """
    completed = []
    i         = lastPos
    n         = len(text)

    depth          = 0   # current brace nesting
    childStart     = -1  # index where the current child object started
    childDepthBase = -1  # depth just before the child's opening brace

    # We need to re-count depth from position 0 each call because
    # lastPos might land inside a string — so we walk from 0 but
    # only yield results after lastPos.
    # For efficiency we pre-count depth up to lastPos first.
    inString   = False
    escape     = False
    for k in range(lastPos):
        ch = text[k]
        if escape:
            escape = False
            continue
        if ch == '\\' and inString:
            escape = True
            continue
        if ch == '"':
            inString = not inString
            continue
        if inString:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1

    # Now walk from lastPos forward
    i        = lastPos
    inString = False
    escape   = False

    while i < n:
        ch = text[i]

        # String tracking to avoid counting braces inside strings
        if escape:
            escape = False
            i += 1
            continue
        if ch == '\\' and inString:
            escape = True
            i += 1
            continue
        if ch == '"':
            inString = not inString
            i += 1
            continue
        if inString:
            i += 1
            continue

        if ch == '{':
            depth += 1
            # Start of a child: depth just became >= 2 (inside root + array)
            if depth >= 2 and childStart == -1:
                childStart     = i
                childDepthBase = depth - 1  # depth before this '{'
        elif ch == '}':
            if childStart != -1 and depth == childDepthBase + 1:
                # This '}' closes the child we started tracking
                childStr = text[childStart : i + 1]
                try:
                    childObj = json.loads(childStr)
                    completed.append(childObj)
                    logger.debug("Incremental child parsed: type=%s", childObj.get("type"))
                except json.JSONDecodeError:
                    pass  # incomplete / malformed fragment — skip
                childStart     = -1
                childDepthBase = -1
                lastPos        = i + 1   # advance checkpoint
            depth -= 1

        i += 1

    return completed, lastPos


def ExtractFullJson(rawText: str) -> dict:
    """
    Extract and parse the first complete JSON object from rawText.
    Strips markdown fences and surrounding prose.
    """
    text  = re.sub(r"```(?:json)?", "", rawText).strip()
    start = text.find("{")
    end   = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in LLM response")
    return json.loads(text[start : end + 1])


# ---------------------------------------------------------------------------
# Ollama streaming generator
# ---------------------------------------------------------------------------

def StreamOllama(userQuery: str):
    """
    Generator yielding SSE strings.

    Event types emitted:
      {"type": "token",     "text": "<raw token>"}
          — every token from Ollama (browser shows char count).
      {"type": "component", "html": "<rendered html>", "id": N}
          — emitted as soon as a complete child JSON object is detected.
      {"type": "done"}
          — stream finished; browser hides typing indicator.
      {"type": "error",     "html": "<alert html>"}
          — fatal error; browser shows the alert and stops.
    """
    prompt  = f"{SYSTEM_PROMPT}\n\nUser request: {userQuery}"
    payload = {
        "model":  CONFIG["MODEL_NAME"],
        "prompt": prompt,
        "stream": True,
    }

    logger.info("Query → Ollama: %s", userQuery[:120])

    accumulated  = ""   # full text received so far
    scanPos      = 0    # position in `accumulated` already scanned for children
    componentIdx = 0    # sequential id for each rendered component

    # ── helper to send an SSE line ──────────────────────────────────────────
    def Sse(payload: dict) -> str:
        return f"data: {json.dumps(payload)}\n\n"

    # ── error helper ────────────────────────────────────────────────────────
    def ErrorEvent(message: str) -> str:
        logger.error(message)
        return Sse({"type": "error",
                    "html": RenderAlert({"type": "alert", "level": "error",
                                         "message": message})})

    # ── stream from Ollama ──────────────────────────────────────────────────
    try:
        with requests.post(
            CONFIG["OLLAMA_URL"],
            json=payload,
            stream=True,
            timeout=CONFIG["REQUEST_TIMEOUT"],
        ) as resp:
            resp.raise_for_status()

            for rawLine in resp.iter_lines():
                if not rawLine:
                    continue

                # Parse the Ollama chunk
                try:
                    chunk = json.loads(rawLine)
                except json.JSONDecodeError:
                    continue

                token = chunk.get("response", "")
                if token:
                    accumulated += token

                    # ── 1. Log every token to file (DEBUG level) ──────────
                    logger.debug("[TOKEN] %s", repr(token))

                    # ── 2. Send token event to browser ────────────────────
                    yield Sse({"type": "token", "text": token})

                    # ── 3. Try to extract newly completed child objects ───
                    newChildren, scanPos = ExtractCompletedChildren(
                        accumulated, scanPos
                    )
                    for child in newChildren:
                        htmlOut = RenderNode(child)
                        logger.info("Streaming component #%d type=%s",
                                    componentIdx, child.get("type"))
                        yield Sse({"type": "component",
                                   "html": htmlOut,
                                   "id":   componentIdx})
                        componentIdx += 1

                if chunk.get("done", False):
                    break

    except requests.exceptions.ConnectionError:
        yield ErrorEvent(
            "Cannot connect to Ollama. Is it running? (ollama serve)"
        )
        return
    except requests.exceptions.Timeout:
        yield ErrorEvent(
            "Ollama request timed out. Try a smaller model or raise REQUEST_TIMEOUT."
        )
        return
    except Exception as exc:
        yield ErrorEvent(f"Streaming error: {exc}")
        logger.debug(traceback.format_exc())
        return

    # ── Log the full accumulated response ───────────────────────────────────
    logger.debug("Full LLM output (%d chars):\n%s", len(accumulated), accumulated)

    # ── If no children were streamed (single non-dashboard component),
    #    parse the whole thing and send it now. ────────────────────────────
    if componentIdx == 0:
        try:
            uiJson  = ExtractFullJson(accumulated)
            htmlOut = RenderNode(uiJson)
            logger.info("Single component rendered: type=%s", uiJson.get("type"))
            yield Sse({"type": "component", "html": htmlOut, "id": 0})
        except Exception as exc:
            logger.warning("JSON parse failed (%s) — falling back to text", exc)
            htmlOut = RenderNode({"type": "text",
                                  "content": accumulated.strip()})
            yield Sse({"type": "component", "html": htmlOut, "id": 0})

    yield Sse({"type": "done"})


# ---------------------------------------------------------------------------
# Inline HTML page template
# ---------------------------------------------------------------------------

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AI Web Emulator</title>
<style>
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
  --font:    'JetBrains Mono','Fira Mono','Cascadia Code',monospace;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{font-family:var(--font);background:var(--bg);color:var(--text);
     display:flex;flex-direction:column;min-height:100vh}

header{padding:1rem 1.5rem;border-bottom:1px solid var(--border);
       display:flex;align-items:center;gap:.75rem;background:var(--surface)}
.logo{font-size:1.1rem;font-weight:700;color:var(--accent);letter-spacing:-.02em}
.sub{color:var(--muted);font-size:.75rem}

.input-bar{padding:1rem 1.5rem;border-bottom:1px solid var(--border);
           display:flex;gap:.5rem;background:var(--surface)}
.input-bar input{flex:1;background:var(--bg);border:1px solid var(--border);
                 border-radius:var(--radius);color:var(--text);
                 font-family:var(--font);font-size:.85rem;
                 padding:.6rem 1rem;outline:none;transition:border-color .2s}
.input-bar input:focus{border-color:var(--accent)}
.input-bar button{background:var(--accent);color:var(--bg);border:none;
                  border-radius:var(--radius);padding:.6rem 1.4rem;
                  font-family:var(--font);font-size:.85rem;font-weight:700;
                  cursor:pointer;transition:opacity .2s}
.input-bar button:hover{opacity:.85}
.input-bar button:disabled{opacity:.4;cursor:not-allowed}

#status{font-size:.72rem;color:var(--muted);padding:.3rem 1.5rem;
        border-bottom:1px solid var(--border);min-height:1.6rem;background:var(--bg)}
#status.thinking{color:var(--accent)}

/* Token stream ticker */
#token-ticker{font-size:.68rem;color:var(--muted);padding:.2rem 1.5rem;
              border-bottom:1px solid var(--border);background:var(--bg);
              white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
              min-height:1.4rem;font-family:var(--font);opacity:0;
              transition:opacity .3s}
#token-ticker.active{opacity:1}

#render-area{flex:1;padding:1.5rem;overflow-y:auto}

/* ── Components ── */
.card{background:var(--surface);border:1px solid var(--border);
      border-radius:var(--radius);padding:1.2rem 1.4rem;
      display:inline-block;min-width:160px;margin:.4rem;
      transition:border-color .2s}
.card:hover{border-color:var(--accent2)}
.card-title{font-size:.78rem;color:var(--muted);text-transform:uppercase;
            letter-spacing:.06em;margin-bottom:.4rem}
.card-value{font-size:2rem;font-weight:700;color:var(--accent)}
.card-subtitle{font-size:.75rem;color:var(--muted);margin-top:.3rem}

.progress-wrap{background:var(--surface);border:1px solid var(--border);
               border-radius:var(--radius);padding:1rem 1.2rem;margin:.4rem 0}
.progress-header{display:flex;justify-content:space-between;
                 font-size:.8rem;color:var(--muted);margin-bottom:.5rem}
.progress-track{background:var(--track);border-radius:99px;height:8px;overflow:hidden}
.progress-fill{height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));
               border-radius:99px;transition:width .6s ease}

.gauge-wrap{display:inline-block;width:130px;margin:.4rem}
.gauge-svg{width:100%}
.gauge-val{fill:var(--text);font-family:var(--font);font-size:18px;font-weight:700}
.gauge-lbl{fill:var(--muted);font-family:var(--font);font-size:10px}

.table-wrap{background:var(--surface);border:1px solid var(--border);
            border-radius:var(--radius);overflow:hidden;margin:.4rem 0}
table{width:100%;border-collapse:collapse;font-size:.82rem}
th{background:var(--track);color:var(--accent);text-align:left;
   padding:.6rem .9rem;font-weight:700;font-size:.72rem;
   text-transform:uppercase;letter-spacing:.05em}
td{padding:.55rem .9rem;border-top:1px solid var(--border)}
tr:hover td{background:var(--track)}

.list-wrap{background:var(--surface);border:1px solid var(--border);
           border-radius:var(--radius);padding:1rem 1.2rem;margin:.4rem 0}
.list-title{font-size:.85rem;color:var(--accent);margin-bottom:.5rem}
ul{list-style:none}
li{padding:.3rem 0;border-bottom:1px solid var(--border);font-size:.82rem}
li:last-child{border:none}
li::before{content:"›";color:var(--accent2);margin-right:.5rem}

.btn{background:transparent;border:1px solid var(--accent2);color:var(--accent2);
     border-radius:var(--radius);padding:.5rem 1.2rem;font-family:var(--font);
     font-size:.82rem;cursor:pointer;margin:.4rem;transition:background .2s,color .2s}
.btn:hover{background:var(--accent2);color:var(--bg)}

.text-block{background:var(--surface);border-left:3px solid var(--accent2);
            padding:.8rem 1rem;border-radius:0 var(--radius) var(--radius) 0;
            font-size:.85rem;line-height:1.6;margin:.4rem 0}

.alert{padding:.75rem 1rem;border-radius:var(--radius);font-size:.82rem;margin:.4rem 0}
.alert-info   {background:#0e2a4a;border:1px solid #1d4ed8}
.alert-success{background:#052e16;border:1px solid #16a34a}
.alert-warning{background:#2d1900;border:1px solid #d97706}
.alert-error  {background:#2d0b0b;border:1px solid #dc2626}

.form-wrap{background:var(--surface);border:1px solid var(--border);
           border-radius:var(--radius);padding:1.2rem;margin:.4rem 0;max-width:420px}
.form-title{font-size:.9rem;color:var(--accent);margin-bottom:.8rem}
.form-field{margin-bottom:.7rem}
.form-field label{display:block;font-size:.75rem;color:var(--muted);margin-bottom:.25rem}
.form-field input{width:100%;background:var(--bg);border:1px solid var(--border);
                  border-radius:8px;color:var(--muted);font-family:var(--font);
                  font-size:.82rem;padding:.45rem .8rem}

.dashboard{width:100%}
.dash-title{font-size:1rem;color:var(--accent);margin-bottom:1rem}
.dash-grid{display:flex;flex-wrap:wrap;gap:.6rem;align-items:flex-start}

/* Typing dots */
.typing{display:inline-flex;gap:4px;align-items:center;padding:.5rem 0}
.typing span{width:6px;height:6px;background:var(--accent);border-radius:50%;
             animation:bounce .9s infinite}
.typing span:nth-child(2){animation-delay:.15s}
.typing span:nth-child(3){animation-delay:.3s}
@keyframes bounce{0%,80%,100%{transform:translateY(0);opacity:.4}
                  40%        {transform:translateY(-6px);opacity:1}}

/* Fade-in for each arriving component */
@keyframes popIn{
  from{opacity:0;transform:translateY(10px) scale(.97)}
  to  {opacity:1;transform:none}
}
.component-enter{animation:popIn .3s ease both}
</style>
</head>
<body>

<header>
  <span class="logo">◈ AI Web Emulator</span>
  <span class="sub">powered by Ollama · JSON UI · live streaming</span>
</header>

<div class="input-bar">
  <input id="queryInput" type="text"
         placeholder='e.g. "Show a CPU/RAM/Disk dashboard"'
         autocomplete="off"/>
  <button id="sendBtn" onclick="SendQuery()">Run ›</button>
</div>

<div id="status">Ready — type a query above and press Run.</div>
<!-- Live token ticker: shows raw tokens as they arrive -->
<div id="token-ticker"></div>

<div id="render-area">
  <div class="alert alert-info">
    ℹ️ Try: <em>"Create a system dashboard"</em> or <em>"Show a weekly tasks table"</em>
  </div>
</div>

<script>
const queryInput  = document.getElementById('queryInput');
const sendBtn     = document.getElementById('sendBtn');
const statusEl    = document.getElementById('status');
const tickerEl    = document.getElementById('token-ticker');
const renderArea  = document.getElementById('render-area');

queryInput.addEventListener('keydown', e => { if (e.key === 'Enter') SendQuery(); });

function SendQuery() {
  const query = queryInput.value.trim();
  if (!query) return;

  sendBtn.disabled   = true;
  statusEl.textContent = '⟳ Connecting to Ollama…';
  statusEl.className   = 'thinking';
  tickerEl.textContent = '';
  tickerEl.className   = 'active';

  // Clear render area, show typing indicator
  renderArea.innerHTML =
    '<div class="typing"><span></span><span></span><span></span></div>';

  const evtSource = new EventSource('/stream?q=' + encodeURIComponent(query));
  let componentCount = 0;

  evtSource.onmessage = function(event) {
    const data = JSON.parse(event.data);

    // ── token: update ticker with the raw text ──────────────────────────
    if (data.type === 'token') {
      tickerEl.textContent = data.text.replace(/\\n/g, ' ');
      statusEl.textContent = '⟳ Generating…';
    }

    // ── component: render it immediately as it arrives ──────────────────
    if (data.type === 'component') {
      // Remove typing indicator on first component
      if (componentCount === 0) {
        renderArea.innerHTML = '';
      }
      const wrapper = document.createElement('div');
      wrapper.className = 'component-enter';
      wrapper.innerHTML = data.html;
      renderArea.appendChild(wrapper);
      componentCount++;
      statusEl.textContent = `⟳ Rendered ${componentCount} component(s)…`;
    }

    // ── error: show alert ───────────────────────────────────────────────
    if (data.type === 'error') {
      renderArea.innerHTML = data.html;
      evtSource.close();
      Finish();
    }

    // ── done: tidy up ───────────────────────────────────────────────────
    if (data.type === 'done') {
      evtSource.close();
      tickerEl.className   = '';
      tickerEl.textContent = '';
      statusEl.textContent = `✓ Done — ${componentCount} component(s) rendered`;
      statusEl.className   = '';
      sendBtn.disabled     = false;
    }
  };

  evtSource.onerror = function() {
    evtSource.close();
    renderArea.innerHTML =
      '<div class="alert alert-error">❌ SSE connection lost. Check server.</div>';
    Finish();
  };

  function Finish() {
    tickerEl.className   = '';
    statusEl.className   = '';
    sendBtn.disabled     = false;
  }
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
    SSE endpoint — ?q=<user query>
    Streams token / component / done / error events.
    """
    userQuery = request.args.get("q", "").strip()
    if not userQuery:
        def emptyGen():
            errNode = {"type": "alert", "level": "warning",
                       "message": "No query provided."}
            yield f"data: {json.dumps({'type':'component','html':RenderNode(errNode),'id':0})}\n\n"
            yield f"data: {json.dumps({'type':'done'})}\n\n"
        return Response(
            stream_with_context(emptyGen()),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return Response(
        stream_with_context(StreamOllama(userQuery)),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting AI Web Emulator on http://%s:%d",
                CONFIG["HOST"], CONFIG["PORT"])
    logger.info("Ollama endpoint : %s", CONFIG["OLLAMA_URL"])
    logger.info("Model           : %s", CONFIG["MODEL_NAME"])
    logger.info("Log dir         : %s/", CONFIG["LOG_DIR"])
    app.run(host=CONFIG["HOST"], port=CONFIG["PORT"], debug=False, threaded=True)
