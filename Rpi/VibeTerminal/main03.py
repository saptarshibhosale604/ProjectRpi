"""
################################################################################
README
################################################################################

# AI-Powered Terminal Emulator (Ollama + Raspberry Pi)

## Overview
A terminal-style interface that accepts natural language queries, sends them to
a locally running Ollama LLM, and streams the response live into the terminal.
The renderer parses special tags in the LLM output to dynamically display rich
UI components such as progress bars, tables, and boxed panels.

## Features
- Every event is logged in real time to  Logs/log-<timestamp>.log
- LLM stats are visible
- Conversation history enable disable

## Architecture
    User Keyboard
         |
         v
    Input Manager       <- reads user query
         |
         v
    Ollama API          <- streams tokens (stream=True)
         |
         v
    Renderer            <- parses tokens, builds/updates UI components
         |
         v
    Display             <- prints live to terminal (ANSI colours)
         |
         v
    Logger              <- writes every event to Logs/log-<timestamp>.log

## Requirements
- Python 3.8+
- Ollama running locally (https://ollama.com)
- A pulled model, e.g.: `ollama pull llama3`
- pip install: requests

## Installation
    pip install requests
    ollama pull llama3   # or any model you prefer

## Usage
    python main.py

    Then type any natural language query, e.g.:
      > Show CPU usage
      > Create a dashboard for system health
      > Display a table of planets

## LLM Output Format (taught via system prompt)
The LLM is instructed to emit special tags that the Renderer interprets:
  [BAR label value_percent]                          -> progress bar
  [TABLE header1,header2 | r1c1,r1c2 | r2c1,r2c2]  -> ASCII table
  [BOX title content]                                -> boxed panel
  Plain text is printed as-is.

## Logging
Each session creates a new file:  Logs/log-<YYYYMMDD_HHMMSS>.log
Log levels used:
  INFO    – normal lifecycle events (startup, query received, response done)
  DEBUG   – per-token / per-line renderer details
  WARNING – recoverable issues (empty input, unknown tag, etc.)
  ERROR   – exceptions caught during Ollama calls or rendering

## Configuration
Edit the constants near the top of main.py:
  OLLAMA_URL   - base URL of your Ollama server
  MODEL_NAME   - Ollama model to use
  MAX_WIDTH    - terminal display width
  LOG_DIR      - directory where log files are written
  LOG_LEVEL    - minimum level written to the log file

## Notes
- Press Ctrl+C at any time to exit.
- Designed for 80-column terminals; works on Raspberry Pi OS terminal.

################################################################################
"""

import sys
import re
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# MODEL_NAME = "llama3.2:1b"                   # model name pulled in Ollama
MODEL_NAME = "llama3.2"                   # model name pulled in Ollama
# MODEL_NAME = "llama2-uncensored:7b"                   # model name pulled in Ollama

USE_CONVERSATION_HISTORY = True # use conversation history in the llm communication

OLLAMA_URL = "http://localhost:11434"   # base URL of local Ollama server
MAX_WIDTH  = 72                         # display width for UI components
LOG_DIR    = "Logs"                     # directory for log files
LOG_LEVEL  = logging.DEBUG              # minimum level captured in log file

# ANSI colour helpers (work on Raspberry Pi OS terminal)
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[32m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
RED    = "\033[31m"
DIM    = "\033[2m"

# Other vars
MODEL_CONTEXT_WINDOW = None

# ---------------------------------------------------------------------------
# Logger setup  –  called once at import time
# ---------------------------------------------------------------------------

def _BuildLogger() -> logging.Logger:
    """
    Create and configure the application logger.

    A new log file is created for every process run, named with the session
    start timestamp so logs are never overwritten.  The file handler flushes
    after every record (via a custom StreamHandler subclass) so entries appear
    in real time even if the process is killed abruptly.

    Returns:
        Configured logging.Logger instance named 'ai_terminal'.
    """
    # Ensure the Logs directory exists
    logDir = Path(LOG_DIR)
    logDir.mkdir(parents=True, exist_ok=True)

    # Build a timestamp-stamped filename for this session
    # sessionTs  = datetime.now().strftime("%Y%m%d_%H%M%S")
    sessionTs  = datetime.now().strftime("%Y%m%d")
    logPath    = logDir / f"log-{sessionTs}.log"

    logger = logging.getLogger("ai_terminal")
    logger.setLevel(LOG_LEVEL)

    # ----- File handler (real-time flush) -----
    class FlushingFileHandler(logging.FileHandler):
        """FileHandler that flushes the stream after every emit."""
        def emit(self, record: logging.LogRecord) -> None:
            super().emit(record)
            self.flush()

    fileFormatter = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fileHandler = FlushingFileHandler(logPath, encoding="utf-8")
    fileHandler.setLevel(LOG_LEVEL)
    fileHandler.setFormatter(fileFormatter)

    # ----- Console handler (WARNING and above only – keep terminal clean) -----
    consoleFormatter = logging.Formatter("%(levelname)s: %(message)s")
    consoleHandler   = logging.StreamHandler(sys.stderr)
    consoleHandler.setLevel(logging.WARNING)
    consoleHandler.setFormatter(consoleFormatter)

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)

    # Log the path so the user knows where to find it
    logger.info("Session started  |  log file: %s", logPath)
    logger.info("Configuration    |  model=%s  ollama=%s  width=%d",
                MODEL_NAME, OLLAMA_URL, MAX_WIDTH)

    return logger


# Module-level logger used everywhere in this file
log = _BuildLogger()

# ---------------------------------------------------------------------------
# System prompt sent to the LLM
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are an AI terminal assistant running on a Raspberry Pi.
Respond concisely. When it makes sense, enrich your response with the
following special tags so the terminal renderer can draw live UI components:

  [BAR <label> <0-100>]
      Draws a labelled progress bar.
      Example: [BAR CPU 43]

  [TABLE <col1>,<col2>,... | <r1c1>,<r1c2>,... | <r2c1>,<r2c2>,...]
      Draws an ASCII table. Columns separated by comma, rows separated by |
      Example: [TABLE Planet,Moons | Earth,1 | Mars,2 | Jupiter,95]

  [BOX <title> <single-line content>]
      Draws a boxed panel with a title.
      Example: [BOX Status System is healthy]

You may mix plain text and tags freely. Each tag must be on its own line.
Keep responses short and practical.
""".strip()

conversationHistory = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }
]

# ---------------------------------------------------------------------------
# Renderer helpers
# ---------------------------------------------------------------------------

def RenderBar(label: str, percent: int, description: str = "") -> str:
    """
    Render a labelled ASCII progress bar.

    Args:
        label:        Text label shown before the bar.
        percent:      Fill percentage (0-100).
        description:  Optional text shown after the percentage.

    Returns:
        A formatted string ready to print.
    """
    percent = max(0, min(100, percent))

    # Reserve space for label and percentage
    barWidth = MAX_WIDTH - len(label) - 10
    barWidth = max(barWidth, 10)

    filled = int(barWidth * percent / 100)
    empty = barWidth - filled
    bar = "█" * filled + "░" * empty

    log.debug(
        "RenderBar  | label=%r  percent=%d  filled=%d  empty=%d  description=%r",
        label,
        percent,
        filled,
        empty,
        description,
    )

    result = (
        f"  {BOLD}{label:<12}{RESET} "
        f"[{GREEN}{bar}{RESET}] {percent:>3}%"
    )

    if description:
        result += f"  {DIM}{description}{RESET}"

    return result

def RenderTable(headerRow: list, dataRows: list) -> str:
    """
    Render a simple ASCII table.

    Args:
        headerRow: List of column header strings.
        dataRows:  List of rows; each row is a list of cell strings.

    Returns:
        A multi-line formatted string.
    """
    allRows   = [headerRow] + dataRows
    colWidths = [max(len(str(cell)) for cell in col) for col in zip(*allRows)]

    def FormatRow(row, bold=False):
        cells = "  ".join(str(cell).ljust(w) for cell, w in zip(row, colWidths))
        return f"  {BOLD if bold else ''}{cells}{RESET}"

    separator = "  " + "-" * (sum(colWidths) + 2 * (len(colWidths) - 1))
    lines     = [separator, FormatRow(headerRow, bold=True), separator]
    for row in dataRows:
        lines.append(FormatRow(row))
    lines.append(separator)

    log.debug("RenderTable | cols=%d  rows=%d  colWidths=%s",
              len(headerRow), len(dataRows), colWidths)

    return "\n".join(lines)


def RenderBox(title: str, content: str) -> str:
    """
    Render a boxed panel with a title.

    Args:
        title:   Box header text.
        content: Body text shown inside the box.

    Returns:
        A multi-line formatted string.
    """
    innerWidth = MAX_WIDTH - 4
    topBorder  = "  ┌" + "─" * (innerWidth + 2) + "┐"
    titleLine  = f"  │ {BOLD}{CYAN}{title.center(innerWidth)}{RESET} │"
    divider    = "  ├" + "─" * (innerWidth + 2) + "┤"
    bodyLine   = f"  │ {content.ljust(innerWidth)} │"
    botBorder  = "  └" + "─" * (innerWidth + 2) + "┘"

    log.debug("RenderBox   | title=%r  content_len=%d", title, len(content))

    return "\n".join([topBorder, titleLine, divider, bodyLine, botBorder])


def RenderLine(rawLine: str) -> None:
    """
    Detect special tags in a single line and print the appropriate component,
    or print the line as plain text.

    Args:
        rawLine: A single line of LLM output (stripped).
    """
    if not rawLine:
        return

    # --- [BAR label percent] ---
    # barMatch = re.match(r"^\[BAR\s+(.+?)\s+(\d+)\]$", rawLine, re.IGNORECASE)
    # barMatch = re.match(r"^\[BAR\s+(.+?)\s+(\d+)%?\]$", rawLine, re.IGNORECASE)
    barMatch = re.match(r"^\[BAR\s+(.+?)\s+(\d+)%?\]\s*(.*)$", rawLine, re.IGNORECASE)
    if barMatch:
        # label, percent = barMatch.group(1), int(barMatch.group(2))
        # label, percent = barMatch.group(1), int(barMatch.group(2))
        # log.info("Renderer    | BAR component  label=%r  percent=%d", label, percent)
        # print(RenderBar(label, percent))
        label = barMatch.group(1)
        percent = int(barMatch.group(2))
        description = barMatch.group(3).strip()

        log.info(
            "Renderer    | BAR component  label=%r  percent=%d  description=%r",
            label,
            percent,
            description,
        )

        print(RenderBar(label, percent, description))
        return


    # --- [TABLE headers | row | row ...] ---
    tableMatch = re.match(r"^\[TABLE\s+(.+)\]$", rawLine, re.IGNORECASE)
    if tableMatch:
        parts     = [p.strip() for p in tableMatch.group(1).split("|")]
        headerRow = [c.strip() for c in parts[0].split(",")]
        dataRows  = [[c.strip() for c in row.split(",")] for row in parts[1:]]
        nCols     = len(headerRow)
        dataRows  = [row + [""] * (nCols - len(row)) for row in dataRows]
        log.info("Renderer    | TABLE component  cols=%d  rows=%d", nCols, len(dataRows))
        print(RenderTable(headerRow, dataRows))
        return

    # --- [BOX title content] ---
    boxMatch = re.match(r"^\[BOX\s+(\S+)\s+(.+)\]$", rawLine, re.IGNORECASE)
    if boxMatch:
        title, content = boxMatch.group(1), boxMatch.group(2)
        log.info("Renderer    | BOX component   title=%r", title)
        print(RenderBox(title, content))
        return

    # Plain text fallback
    log.debug("Renderer    | plain text  %r", rawLine[:80])
    print(f"  {rawLine}")


# ---------------------------------------------------------------------------
# Ollama streaming
# ---------------------------------------------------------------------------

def GetModelContextWindow() -> int:
    """
    Query Ollama for the model metadata and return its context window.

    Returns:
        int: Context window size (tokens).

    Raises:
        RuntimeError: If the context window cannot be determined.
    """

    url = f"{OLLAMA_URL}/api/show"

    payload = {
        "model": MODEL_NAME
    }

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()

    #
    # Depending on the Ollama version, the context length may appear
    # in different locations. Search common locations.
    #

    candidates = []

    # Example:
    # {
    #   "model_info": {
    #       "llama.context_length": 8192
    #   }
    # }
    model_info = data.get("model_info", {})
    if isinstance(model_info, dict):
        for key, value in model_info.items():
            if (
                "context" in key.lower()
                and isinstance(value, int)
            ):
                candidates.append(value)

    # Example:
    # {
    #     "parameters": "... num_ctx 8192 ..."
    # }
    parameters = data.get("parameters", "")
    if isinstance(parameters, str):
        import re

        match = re.search(
            r"num_ctx\s+(\d+)",
            parameters,
            flags=re.IGNORECASE,
        )

        if match:
            candidates.append(int(match.group(1)))

    if not candidates:
        raise RuntimeError(
            f"Could not determine context window for model '{MODEL_NAME}'."
        )

    context_window = max(candidates)

    log.info(
        "Model=%s  Context Window=%d tokens",
        MODEL_NAME,
        context_window,
    )

    return context_window


def StreamOllama(userQuery: str) -> None:
    """
    Send the user query to the local Ollama API and stream the response,
    printing each token live and passing complete lines to RenderLine.

    Args:
        userQuery: The natural language query from the user.
    """
    url     = f"{OLLAMA_URL}/api/chat"
    # url     = f"{OLLAMA_URL}/api/generate"

    if USE_CONVERSATION_HISTORY:
        # Copy existing history and append current user message
        messages = conversationHistory.copy()
        messages.append({
            "role": "user",
            "content": userQuery,
        })
    else:
        # Existing behavior
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": userQuery,
            },
        ]

    payload = {
        "model":    MODEL_NAME,
        "stream":   True,
        "messages": messages,
    }

    log.info("OllamaAPI   | POST %s  model=%s  query=%r", url, MODEL_NAME, userQuery[:120])

    try:
        # with requests.post(url, json=payload, stream=True, timeout=60) as response:
        with requests.post(url, json=payload, stream=True, timeout=600) as response:
            response.raise_for_status()
            log.info("OllamaAPI   | connection established  HTTP %d", response.status_code)

            print(f"\n{CYAN}{'─' * MAX_WIDTH}{RESET}")
            print(f"  {BOLD}{YELLOW}Assistant:{RESET}")

            lineBuffer  = ""      # accumulates characters until a newline
            tokenCount  = 0       # total tokens received this turn

            fullResponse = ""

            for chunk in response.iter_lines():
                if not chunk:
                    continue

                try:
                    data = json.loads(chunk)
                except json.JSONDecodeError as jsonErr:
                    log.warning("OllamaAPI   | JSON decode failed  chunk=%r  err=%s",
                                chunk[:60], jsonErr)
                    continue

                # Extract token text
                token = ""
                if "message" in data and "content" in data["message"]:
                    token = data["message"]["content"]

                # Statistics returned by the final chunk
                stats = None

                if not token:
                    if data.get("done"):
                        stats = data
                        log.info("OllamaAPI   | stream done signal received")
                        break
                    continue

                tokenCount += 1
                log.debug("Token #%-4d | %r", tokenCount, token)

                fullResponse += token

                # Accumulate into buffer; flush complete lines to renderer
                lineBuffer += token
                while "\n" in lineBuffer:
                    completeLine, lineBuffer = lineBuffer.split("\n", 1)
                    RenderLine(completeLine.strip())

            # Flush any trailing content without a final newline
            if lineBuffer.strip():
                RenderLine(lineBuffer.strip())

            if USE_CONVERSATION_HISTORY:
                conversationHistory.append({
                    "role": "user",
                    "content": userQuery,
                })

                conversationHistory.append({
                    "role": "assistant",
                    "content": fullResponse,
                })

            log.info(
                "==================== OLLAMA REQUEST ====================\n%s",
                json.dumps(payload, indent=2)
            )

            log.info(
                "==================== OLLAMA RESPONSE ===================\n%s",
                fullResponse
            )

            if stats:
                prompt_tokens = stats.get("prompt_eval_count", 0)
                completion_tokens = stats.get("eval_count", 0)

                prompt_duration = stats.get("prompt_eval_duration", 0) / 1e9
                completion_duration = stats.get("eval_duration", 0) / 1e9
                total_duration = stats.get("total_duration", 0) / 1e9
                load_duration = stats.get("load_duration", 0) / 1e9

                prompt_tps = (
                    prompt_tokens / prompt_duration
                    if prompt_duration > 0 else 0
                )

                completion_tps = (
                    completion_tokens / completion_duration
                    if completion_duration > 0 else 0
                )

                used_context = prompt_tokens

                remaining_context = (
                    max(MODEL_CONTEXT_WINDOW - used_context, 0)
                    if MODEL_CONTEXT_WINDOW
                    else 0
                )

                context_usage_percent = (
                    used_context * 100 / MODEL_CONTEXT_WINDOW
                    if MODEL_CONTEXT_WINDOW
                    else 0
                )

                log.info(
                    "\n"
                    "==================== LLM STATS ====================\n"
                    "Prompt Tokens      : %d\n"
                    "Completion Tokens  : %d\n"
                    "Total Tokens       : %d\n"
                    "\n"
                    "Context Window     : %d\n"
                    "Used Context       : %d\n"
                    "Remaining Context  : %d\n"
                    "Context Usage      : %.2f%%\n"
                    "\n"
                    "Prompt Time        : %.3f sec\n"
                    "Generation Time    : %.3f sec\n"
                    "Load Time          : %.3f sec\n"
                    "Total Time         : %.3f sec\n"
                    "Prompt Speed       : %.2f tok/s\n"
                    "Generation Speed   : %.2f tok/s\n"
                    "===================================================",
                    prompt_tokens,
                    completion_tokens,
                    prompt_tokens + completion_tokens,
                    MODEL_CONTEXT_WINDOW,
                    used_context,
                    remaining_context,
                    context_usage_percent,
                    prompt_duration,
                    completion_duration,
                    load_duration,
                    total_duration,
                    prompt_tps,
                    completion_tps,
                )

            print(f"{CYAN}{'─' * MAX_WIDTH}{RESET}\n")
            log.info("OllamaAPI   | response complete  tokens_received=%d", tokenCount)

    except requests.exceptions.ConnectionError as connErr:
        log.error("OllamaAPI   | ConnectionError: %s", connErr)
        print(f"\n  {RED}Error:{RESET} Cannot connect to Ollama at {OLLAMA_URL}.")
        print(f"  Make sure Ollama is running: {DIM}ollama serve{RESET}\n")

    except requests.exceptions.Timeout as timeoutErr:
        log.error("OllamaAPI   | Timeout: %s", timeoutErr)
        print(f"\n  {RED}Error:{RESET} Request to Ollama timed out.\n")

    except requests.exceptions.HTTPError as httpErr:
        log.error("OllamaAPI   | HTTPError: %s", httpErr)
        print(f"\n  {RED}HTTP Error:{RESET} {httpErr}\n")

    except Exception as err:
        log.exception("OllamaAPI   | Unexpected error: %s", err)
        print(f"\n  {RED}Unexpected error:{RESET} {err}\n")


def MockOllamaFromFile(userQuery: str = "") -> None:
    """
    Mimics an Ollama response by reading `input.txt`
    and sending each line to RenderLine().

    Args:
        userQuery: Ignored. Present only to keep the
                   same signature as StreamOllama().
    """
    log.info("MockOllama  | Reading response from input.txt")

    try:
        print(f"\n{CYAN}{'─' * MAX_WIDTH}{RESET}")
        print(f"  {BOLD}{YELLOW}Assistant:{RESET}")

        lineBuffer = ""
        fullResponse = ""

        with open("input.txt", "r", encoding="utf-8") as f:
            fullResponse = f.read()

        lineBuffer += fullResponse

        while "\n" in lineBuffer:
            completeLine, lineBuffer = lineBuffer.split("\n", 1)
            RenderLine(completeLine.strip())

        # Flush any remaining content
        if lineBuffer.strip():
            RenderLine(lineBuffer.strip())

        log.info(
            "==================== MOCK RESPONSE ====================\n%s",
            fullResponse,
        )

        print(f"{CYAN}{'─' * MAX_WIDTH}{RESET}\n")
        log.info("MockOllama  | response complete")

    except FileNotFoundError:
        log.error("MockOllama  | input.txt not found")
        print(f"\n{RED}Error:{RESET} input.txt not found.\n")

    except Exception as err:
        log.exception("MockOllama  | Unexpected error: %s", err)
        print(f"\n{RED}Unexpected error:{RESET} {err}\n")

# ---------------------------------------------------------------------------
# Input Manager
# ---------------------------------------------------------------------------

def PrintWelcome() -> None:
    """Print the welcome banner on startup."""
    banner = f"""
{CYAN}{'═' * MAX_WIDTH}
  {'AI TERMINAL':^{MAX_WIDTH - 4}}
  {'Powered by Ollama  •  Raspberry Pi':^{MAX_WIDTH - 4}}
{'═' * MAX_WIDTH}{RESET}
  Config:
    {DIM}> OLLAMA_URL → {OLLAMA_URL}
    > Logs → {DIM}{LOG_DIR}/{RESET}
    > MODEL_NAME → {MODEL_NAME} {RESET}

  Type a natural language query and press Enter.
  Examples:
    {DIM}> Show CPU and RAM usage
    > Create a table of the 5 largest planets
    > Give me a quick system health summary{RESET}

  Press {BOLD}Ctrl+C{RESET} to exit.
{CYAN}{'─' * MAX_WIDTH}{RESET}
"""
    print(banner)
    log.info("Welcome banner printed")


def ReadInput() -> str:
    """
    Display a prompt and read a line of input from the user.

    Returns:
        The stripped input string, or empty string on EOF.
    """
    try:
        userInput = input(f"{BOLD}{GREEN}>{RESET} ").strip()
        return userInput
    except EOFError:
        log.warning("InputManager | EOF on stdin")
        return ""


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def Main() -> None:
    """
    Entry point.  Runs the interactive query loop:
      1. Print welcome banner.
      2. Read user query.
      3. Stream LLM response through the renderer.
      4. Repeat.
    """
    global MODEL_CONTEXT_WINDOW
    PrintWelcome()
    queryCount = 0   # how many queries handled this session
    try:
        MODEL_CONTEXT_WINDOW = GetModelContextWindow()
    except Exception as err:
        log.warning(
            "Failed to fetch context window: %s",
            err,
        )

        MODEL_CONTEXT_WINDOW = 0

    while True:
        try:
            userQuery = ReadInput()

            if not userQuery:
                log.debug("InputManager | empty input, skipping")
                continue

            if userQuery.lower() in ("exit", "quit", "q"):
                log.info("Session ended by user  |  total queries=%d", queryCount)
                print(f"\n  {DIM}Goodbye.{RESET}\n")
                sys.exit(0)

            queryCount += 1
            log.info("InputManager | query #%d received: %r", queryCount, userQuery[:120])
            StreamOllama(userQuery)
            # MockOllamaFromFile(userQuery)


        except KeyboardInterrupt:
            log.info("Session interrupted (KeyboardInterrupt)  |  total queries=%d",
                     queryCount)
            print(f"\n\n  {DIM}Interrupted. Goodbye.{RESET}\n")
            sys.exit(0)


if __name__ == "__main__":
    Main()
