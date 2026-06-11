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
    Display             <- prints live to terminal via curses

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
  [BAR label value_percent]       -> progress bar
  [TABLE header1,header2 | r1c1,r1c2 | r2c1,r2c2]  -> ASCII table
  [BOX title content]             -> boxed panel
  Plain text is printed as-is.

## Configuration
Edit the constants near the top of main.py:
  OLLAMA_URL   - base URL of your Ollama server
  MODEL_NAME   - Ollama model to use
  MAX_WIDTH    - terminal display width

## Notes
- Press Ctrl+C at any time to exit.
- Designed for 80-column terminals; works on Raspberry Pi OS terminal.

################################################################################
"""

import sys
import re
import time
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_URL = "http://localhost:11434"   # base URL of local Ollama server
# MODEL_NAME = "llama3"                   # model name pulled in Ollama
# MODEL_NAME = "llama3.2:1b"                   # model name pulled in Ollama
MODEL_NAME = "llama3.2"                   # model name pulled in Ollama
MAX_WIDTH  = 72                         # display width for UI components

# ANSI colour helpers (work on Raspberry Pi OS terminal)
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[32m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
RED    = "\033[31m"
DIM    = "\033[2m"

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

# ---------------------------------------------------------------------------
# Renderer helpers
# ---------------------------------------------------------------------------

def RenderBar(label: str, percent: int) -> str:
    """
    Render a labelled ASCII progress bar.

    Args:
        label:   Text label shown before the bar.
        percent: Fill percentage (0-100).

    Returns:
        A formatted string ready to print.
    """
    percent = max(0, min(100, percent))
    barWidth = MAX_WIDTH - len(label) - 10   # reserve space for label + number
    filled   = int(barWidth * percent / 100)
    empty    = barWidth - filled
    bar      = "█" * filled + "░" * empty
    return f"  {BOLD}{label:<12}{RESET} [{GREEN}{bar}{RESET}] {percent:>3}%"


def RenderTable(headerRow: list[str], dataRows: list[list[str]]) -> str:
    """
    Render a simple ASCII table.

    Args:
        headerRow: List of column header strings.
        dataRows:  List of rows; each row is a list of cell strings.

    Returns:
        A multi-line formatted string.
    """
    # Compute column widths
    allRows    = [headerRow] + dataRows
    colWidths  = [max(len(str(cell)) for cell in col) for col in zip(*allRows)]

    def FormatRow(row, bold=False):
        cells = "  ".join(str(cell).ljust(w) for cell, w in zip(row, colWidths))
        return f"  {BOLD if bold else ''}{cells}{RESET}"

    separator = "  " + "-" * (sum(colWidths) + 2 * (len(colWidths) - 1))
    lines = [separator, FormatRow(headerRow, bold=True), separator]
    for row in dataRows:
        lines.append(FormatRow(row))
    lines.append(separator)
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
    return "\n".join([topBorder, titleLine, divider, bodyLine, botBorder])


def RenderLine(rawLine: str) -> None:
    """
    Detect special tags in a single line and print the appropriate component,
    or print the line as plain text.

    Args:
        rawLine: A single line of LLM output (stripped).
    """
    # --- [BAR label percent] ---
    barMatch = re.match(r"^\[BAR\s+(.+?)\s+(\d+)\]$", rawLine, re.IGNORECASE)
    if barMatch:
        label   = barMatch.group(1)
        percent = int(barMatch.group(2))
        print(RenderBar(label, percent))
        return

    # --- [TABLE headers | row | row ...] ---
    tableMatch = re.match(r"^\[TABLE\s+(.+)\]$", rawLine, re.IGNORECASE)
    if tableMatch:
        parts     = [p.strip() for p in tableMatch.group(1).split("|")]
        headerRow = [c.strip() for c in parts[0].split(",")]
        dataRows  = [[c.strip() for c in row.split(",")] for row in parts[1:]]
        # Pad rows that are shorter than header
        nCols = len(headerRow)
        dataRows = [row + [""] * (nCols - len(row)) for row in dataRows]
        print(RenderTable(headerRow, dataRows))
        return

    # --- [BOX title content] ---
    boxMatch = re.match(r"^\[BOX\s+(\S+)\s+(.+)\]$", rawLine, re.IGNORECASE)
    if boxMatch:
        title   = boxMatch.group(1)
        content = boxMatch.group(2)
        print(RenderBox(title, content))
        return

    # Plain text
    if rawLine:
        print(f"  {rawLine}")


# ---------------------------------------------------------------------------
# Ollama streaming
# ---------------------------------------------------------------------------

def StreamOllama(userQuery: str) -> None:
    """
    Send the user query to the local Ollama API and stream the response,
    printing each token live and passing complete lines to RenderLine.

    Args:
        userQuery: The natural language query from the user.
    """
    url     = f"{OLLAMA_URL}/api/chat"
    payload = {
        "model": MODEL_NAME,
        "stream": True,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": userQuery},
        ],
    }

    try:
        with requests.post(url, json=payload, stream=True, timeout=60) as response:
            response.raise_for_status()

            print(f"\n{CYAN}{'─' * MAX_WIDTH}{RESET}")
            print(f"  {BOLD}{YELLOW}Assistant:{RESET}")

            lineBuffer = ""  # accumulates characters until a newline

            for chunk in response.iter_lines():
                if not chunk:
                    continue

                import json as _json
                try:
                    data = _json.loads(chunk)
                except _json.JSONDecodeError:
                    continue

                # Extract the token text
                token = ""
                if "message" in data and "content" in data["message"]:
                    token = data["message"]["content"]

                if not token:
                    # Check for done signal
                    if data.get("done"):
                        break
                    continue

                # Accumulate into buffer; flush complete lines
                lineBuffer += token
                while "\n" in lineBuffer:
                    completeLine, lineBuffer = lineBuffer.split("\n", 1)
                    RenderLine(completeLine.strip())

            # Flush any remaining content without a trailing newline
            if lineBuffer.strip():
                RenderLine(lineBuffer.strip())

            print(f"{CYAN}{'─' * MAX_WIDTH}{RESET}\n")

    except requests.exceptions.ConnectionError:
        print(f"\n  {RED}Error:{RESET} Cannot connect to Ollama at {OLLAMA_URL}.")
        print(f"  Make sure Ollama is running: {DIM}ollama serve{RESET}\n")

    except requests.exceptions.Timeout:
        print(f"\n  {RED}Error:{RESET} Request to Ollama timed out.\n")

    except requests.exceptions.HTTPError as httpErr:
        print(f"\n  {RED}HTTP Error:{RESET} {httpErr}\n")

    except Exception as err:
        print(f"\n  {RED}Unexpected error:{RESET} {err}\n")


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
  Type a natural language query and press Enter.
  Examples:
    {DIM}> Show CPU and RAM usage
    > Create a table of the 5 largest planets
    > Give me a quick system health summary{RESET}

  Press {BOLD}Ctrl+C{RESET} to exit.
{CYAN}{'─' * MAX_WIDTH}{RESET}
"""
    print(banner)


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
    PrintWelcome()

    while True:
        try:
            userQuery = ReadInput()

            if not userQuery:
                continue  # ignore empty input

            if userQuery.lower() in ("exit", "quit", "q"):
                print(f"\n  {DIM}Goodbye.{RESET}\n")
                sys.exit(0)

            StreamOllama(userQuery)

        except KeyboardInterrupt:
            print(f"\n\n  {DIM}Interrupted. Goodbye.{RESET}\n")
            sys.exit(0)


if __name__ == "__main__":
    Main()
