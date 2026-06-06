"""
================================================================================
README
================================================================================
# AI-Powered Terminal Emulator with Game Selector
# ================================================
#
# DESCRIPTION:
#   A curses-based terminal UI for Raspberry Pi that uses a local Ollama LLM
#   to process natural language and lets you play two simple games.
#   Runs entirely inside an SSH session or bare terminal — no $DISPLAY needed.
#
# ARCHITECTURE:
#   User Keyboard → Input Manager → Ollama API (stream=True)
#                                         ↓
#                              Renderer → curses Display
#                                         ↓
#                                    Logger → Logs/log-<date>.log
#
# REQUIREMENTS:
#   - Python 3.8+
#   - Ollama installed and running  →  https://ollama.com
#   - A 2B model pulled            →  ollama pull gemma2:2b
#   - pip install requests
#   - curses is part of the Python standard library (no install needed)
#
# USAGE:
#   python main.py
#
# LOG FILES:
#   Logs are written to  Logs/log-YYYY-MM-DD.log  (auto-created).
#
# GAMES:
#   1. Number Guessing  – guess the secret number (1-100) with AI taunts,
#                         hot/cold hints, and a per-session leaderboard.
#   2. Riddle Quiz      – solve AI riddles; earn streaks, get hints after
#                         3 wrong answers, and see your score grow.
#
# COMMANDS (type in the input box):
#   1 / play number game   → Number Guessing Game
#   2 / play riddle game   → Riddle Quiz
#   menu / back            → Return to game selector
#   help                   → Show available commands
#   hint                   → (Number game) ask for a range hint
#   skip                   → (Riddle mode) next riddle
#   score                  → Show current session score
#   <anything else>        → Ask the AI a question
#   Ctrl+C                 → Quit
================================================================================
"""

import curses
import threading
import requests
import json
import random
import textwrap
import time
import os
import logging
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
CONFIG = {
    "ollamaHost":  "http://localhost:11434",
    # "model":       "gemma2:2b",
    "model":        "llama3.2",
    # MODEL_NAME = "llama3.2:1b"                   # model name pulled in Ollama
    # MODEL_NAME = "llama3.2"                   # model name pulled in Ollama
    # MODEL_NAME = "llama2-uncensored:7b"                   # model name pulled in Ollama

    "maxLines":    600,           # scroll-back buffer size
    "logDir":      "Logs",        # log folder (relative to script)
}

# ──────────────────────────────────────────────────────────────────────────────
# COLOUR PAIR IDs
# ──────────────────────────────────────────────────────────────────────────────
C_NORMAL  = 1   # green on black  — default text
C_CYAN    = 2   # cyan on black   — AI / prompts / headers
C_YELLOW  = 3   # yellow on black — warnings / boxes / hints
C_RED     = 4   # red on black    — errors / wrong answers
C_WHITE   = 5   # white on black  — body text
C_DIM     = 6   # dark grey       — hints / status text
C_INPUT   = 7   # black on green  — input bar
C_STATUS  = 8   # black on cyan   — status bar
C_MAGENTA = 9   # magenta         — streaks / special events

# ──────────────────────────────────────────────────────────────────────────────
# SESSION SCORE  (persists for the whole run)
# ──────────────────────────────────────────────────────────────────────────────
sessionScore = {
    "numberWins":   0,
    "numberBest":   None,    # fewest attempts ever
    "riddleWins":   0,
    "riddleStreak": 0,
    "riddleBest":   0,       # longest streak
    "hintsUsed":    0,
}

# ──────────────────────────────────────────────────────────────────────────────
# GAME STATE
# ──────────────────────────────────────────────────────────────────────────────
gameState = {
    "mode":          "menu",   # "menu" | "number" | "riddle"
    "secretNumber":  None,
    "attempts":      0,
    "wrongAnswers":  0,        # riddle wrong-answer counter (for hints)
    "riddleAnswer":  None,
    "riddleHint":    None,     # AI-generated hint for current riddle
    "riddleActive":  False,
    "hintGiven":     False,    # whether hint was already revealed this riddle
    "numberLow":     1,        # narrowing range for number game
    "numberHigh":    100,
}


# ──────────────────────────────────────────────────────────────────────────────
# LOGGER
# ──────────────────────────────────────────────────────────────────────────────

class GameLogger:
    """
    Writes timestamped log entries to  Logs/log-YYYY-MM-DD.log.
    Thread-safe — multiple threads may call Log() simultaneously.
    """

    def __init__(self, logDir=CONFIG["logDir"]):
        """
        Initialise the logger, creating the Logs directory if needed.

        Args:
            logDir: Path to the folder where log files are stored.
        """
        os.makedirs(logDir, exist_ok=True)
        dateStamp = datetime.now().strftime("%Y-%m-%d")
        logPath   = os.path.join(logDir, f"log-{dateStamp}.log")

        self._logger = logging.getLogger("AITerminal")
        self._logger.setLevel(logging.DEBUG)

        # Avoid adding duplicate handlers on re-import
        if not self._logger.handlers:
            handler = logging.FileHandler(logPath, encoding="utf-8")
            handler.setFormatter(
                logging.Formatter("%(asctime)s  [%(levelname)s]  %(message)s",
                                  datefmt="%H:%M:%S")
            )
            self._logger.addHandler(handler)

        self.Log("INFO", f"Session started — log file: {logPath}")

    def Log(self, level, message):
        """
        Write a log entry.

        Args:
            level  : "INFO" | "DEBUG" | "WARNING" | "ERROR"
            message: Log message string.
        """
        level = level.upper()
        if   level == "DEBUG":   self._logger.debug(message)
        elif level == "WARNING": self._logger.warning(message)
        elif level == "ERROR":   self._logger.error(message)
        else:                    self._logger.info(message)

    def Close(self):
        """Flush and close all handlers."""
        self.Log("INFO", "Session ended.")
        for h in self._logger.handlers:
            h.flush()
            h.close()


# ──────────────────────────────────────────────────────────────────────────────
# OLLAMA HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def StreamOllama(prompt, onToken, systemPrompt=None, logger=None):
    """
    Stream tokens from the local Ollama /api/generate endpoint.

    Args:
        prompt      : User prompt string.
        onToken     : Callable(token: str) — invoked for every streamed token.
        systemPrompt: Optional system prompt string.
        logger      : Optional GameLogger instance for debug logging.
    """
    payload = {"model": CONFIG["model"], "prompt": prompt, "stream": True}
    if systemPrompt:
        payload["system"] = systemPrompt

    if logger:
        logger.Log("DEBUG", f"Ollama request: {prompt[:120]}")

    try:
        with requests.post(
            f"{CONFIG['ollamaHost']}/api/generate",
            json=payload, stream=True, timeout=120,
        ) as resp:
            resp.raise_for_status()
            fullResponse = []
            for rawLine in resp.iter_lines():
                if rawLine:
                    try:
                        chunk = json.loads(rawLine)
                        token = chunk.get("response", "")
                        if token:
                            onToken(token)
                            fullResponse.append(token)
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        pass
            if logger:
                logger.Log("DEBUG", f"Ollama response: {''.join(fullResponse)[:200]}")

    except requests.exceptions.ConnectionError:
        msg = "\n[ERROR] Cannot connect to Ollama — run: ollama serve\n"
        onToken(msg)
        if logger:
            logger.Log("ERROR", "Ollama connection refused")
    except requests.exceptions.Timeout:
        onToken("\n[ERROR] Ollama request timed out.\n")
        if logger:
            logger.Log("ERROR", "Ollama timeout")
    except Exception as exc:
        onToken(f"\n[ERROR] {exc}\n")
        if logger:
            logger.Log("ERROR", str(exc))


# ──────────────────────────────────────────────────────────────────────────────
# SCROLL BUFFER
# ──────────────────────────────────────────────────────────────────────────────

class ScrollBuffer:
    """Thread-safe display buffer; tokens stream into the last open line."""

    def __init__(self, maxLines=600):
        self._lines    = []
        self._lock     = threading.Lock()
        self._maxLines = maxLines
        self._dirty    = True

    def Append(self, text, colorId=C_NORMAL):
        """
        Add text to buffer. Tokens with the same colour and no trailing newline
        are merged into the existing last line so streaming looks smooth.

        Args:
            text    : String (may contain newlines).
            colorId : Curses colour-pair ID.
        """
        with self._lock:
            if (self._lines
                    and self._lines[-1][1] == colorId
                    and not self._lines[-1][0].endswith("\n")):
                self._lines[-1] = (self._lines[-1][0] + text, colorId)
            else:
                self._lines.append((text, colorId))
            if len(self._lines) > self._maxLines:
                self._lines = self._lines[-self._maxLines:]
            self._dirty = True

    def Clear(self):
        with self._lock:
            self._lines = []
            self._dirty = True

    def GetLines(self):
        with self._lock:
            return list(self._lines)

    def IsDirty(self):
        with self._lock:
            d = self._dirty
            self._dirty = False
            return d


# ──────────────────────────────────────────────────────────────────────────────
# CURSES APPLICATION
# ──────────────────────────────────────────────────────────────────────────────

class TerminalApp:
    """
    Main application — owns the curses stdscr and all sub-windows.

    Layout (rows top to bottom):
      [0]        status bar  (model / host)
      [1..H-3]   scroll area (game output)
      [H-2]      stats bar   (mode / score / streak)
      [H-1]      input bar
    """

    def __init__(self, stdscr):
        """Initialise curses, logger, windows, welcome screen, event loop."""
        self.stdscr   = stdscr
        self.buf      = ScrollBuffer(CONFIG["maxLines"])
        self.inputStr = ""
        self.busy     = False
        self.running  = True
        self.logger   = GameLogger(CONFIG["logDir"])

        self._InitCurses()
        self._BuildWindows()
        self._ShowWelcome()
        self._Loop()

    # ── Curses setup ──────────────────────────────────────────────────────────

    def _InitCurses(self):
        """Configure colours, cursor behaviour, and non-blocking getch."""
        curses.curs_set(1)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)

        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(C_NORMAL,  curses.COLOR_GREEN,   -1)
        curses.init_pair(C_CYAN,    curses.COLOR_CYAN,    -1)
        curses.init_pair(C_YELLOW,  curses.COLOR_YELLOW,  -1)
        curses.init_pair(C_RED,     curses.COLOR_RED,     -1)
        curses.init_pair(C_WHITE,   curses.COLOR_WHITE,   -1)
        curses.init_pair(C_DIM,     8,                    -1)
        curses.init_pair(C_INPUT,   curses.COLOR_BLACK,   curses.COLOR_GREEN)
        curses.init_pair(C_STATUS,  curses.COLOR_BLACK,   curses.COLOR_CYAN)
        curses.init_pair(C_MAGENTA, curses.COLOR_MAGENTA, -1)

    def _BuildWindows(self):
        """Create sub-windows sized to the current terminal dimensions."""
        self.H, self.W = self.stdscr.getmaxyx()
        self.scrollH   = max(1, self.H - 3)

        self.statusWin = curses.newwin(1, self.W, 0, 0)
        self.scrollWin = curses.newwin(self.scrollH, self.W, 1, 0)
        self.scrollWin.scrollok(True)
        self.statsWin  = curses.newwin(1, self.W, self.H - 2, 0)
        self.inputWin  = curses.newwin(1, self.W, self.H - 1, 0)

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _Render(self):
        """Redraw all four UI bands."""
        self._DrawStatusBar()
        self._DrawScrollArea()
        self._DrawStatsBar()
        self._DrawInputBar()

    def _DrawStatusBar(self):
        text = (f" AI TERMINAL  |  model: {CONFIG['model']}"
                f"  |  {CONFIG['ollamaHost']} ")
        self.statusWin.erase()
        self.statusWin.bkgd(" ", curses.color_pair(C_STATUS))
        try:
            self.statusWin.addnstr(0, 0, text.ljust(self.W), self.W,
                                   curses.color_pair(C_STATUS) | curses.A_BOLD)
        except curses.error:
            pass
        self.statusWin.noutrefresh()

    def _DrawStatsBar(self):
        """Bottom bar: mode, score counters, streak indicator."""
        mode    = gameState["mode"].upper()
        nWins   = sessionScore["numberWins"]
        rWins   = sessionScore["riddleWins"]
        streak  = sessionScore["riddleStreak"]
        best    = sessionScore["numberBest"]
        bestStr = f"  best:{best}atts" if best else ""
        streakStar = " *STREAK*" if streak >= 3 else ""

        text = (f"  MODE:{mode}  |  Num wins:{nWins}{bestStr}"
                f"  |  Riddle wins:{rWins}  streak:{streak}{streakStar}"
                f"  |  Ctrl+C quit")
        self.statsWin.erase()
        self.statsWin.bkgd(" ", curses.color_pair(C_INPUT))
        try:
            self.statsWin.addnstr(0, 0, text.ljust(self.W), self.W,
                                  curses.color_pair(C_INPUT))
        except curses.error:
            pass
        self.statsWin.noutrefresh()

    def _DrawScrollArea(self):
        """Word-wrap buffer entries; show the last scrollH lines."""
        self.scrollWin.erase()
        self.scrollWin.bkgd(" ", curses.color_pair(C_NORMAL))

        displayLines = []
        for rawText, colorId in self.buf.GetLines():
            for segment in rawText.split("\n"):
                if not segment:
                    displayLines.append(("", colorId))
                else:
                    for wLine in (textwrap.wrap(segment, self.W - 1) or [""]):
                        displayLines.append((wLine, colorId))

        visible = displayLines[-self.scrollH:]
        for rowIdx, (line, colorId) in enumerate(visible):
            if rowIdx >= self.scrollH:
                break
            try:
                self.scrollWin.addnstr(rowIdx, 0, line, self.W - 1,
                                       curses.color_pair(colorId))
            except curses.error:
                pass
        self.scrollWin.noutrefresh()

    def _DrawInputBar(self):
        """Prompt arrow and current typed string."""
        prefix  = ">>> " if not self.busy else "... "
        display = (prefix + self.inputStr)[-(self.W - 1):]
        self.inputWin.erase()
        self.inputWin.bkgd(" ", curses.color_pair(C_NORMAL))
        try:
            self.inputWin.addnstr(0, 0, display.ljust(self.W - 1),
                                  self.W - 1,
                                  curses.color_pair(C_NORMAL) | curses.A_BOLD)
            self.inputWin.move(0, min(len(display), self.W - 2))
        except curses.error:
            pass
        self.inputWin.noutrefresh()

    # ── Write helpers (thread-safe) ───────────────────────────────────────────

    def Write(self, text, colorId=C_NORMAL):
        """Append text to scroll buffer."""
        self.buf.Append(text, colorId)

    def Writeln(self, text="", colorId=C_NORMAL):
        """Append text + newline to scroll buffer."""
        self.buf.Append(text + "\n", colorId)

    def ClearBuf(self):
        """Wipe the scroll buffer."""
        self.buf.Clear()

    # ── Event loop ────────────────────────────────────────────────────────────

    def _Loop(self):
        """Non-blocking ~60 fps event loop; redraws only when dirty."""
        prevInput = None
        while self.running:
            self._HandleResize()
            dirty = self.buf.IsDirty()
            if dirty or self.inputStr != prevInput:
                self._Render()
                curses.doupdate()
                prevInput = self.inputStr

            try:
                ch = self.stdscr.getch()
            except Exception:
                ch = -1

            if ch == -1:
                time.sleep(0.016)
                continue

            if ch in (10, 13, curses.KEY_ENTER):
                self._OnEnter()
            elif ch in (127, curses.KEY_BACKSPACE, 8):
                self.inputStr = self.inputStr[:-1]
            elif ch == 3:                              # Ctrl+C
                self.running = False
            elif 32 <= ch <= 126:
                self.inputStr += chr(ch)

        # Cleanup
        self.logger.Close()

    def _HandleResize(self):
        """Rebuild windows when terminal is resized."""
        newH, newW = self.stdscr.getmaxyx()
        if newH != self.H or newW != self.W:
            self.H, self.W = newH, newW
            curses.resizeterm(newH, newW)
            self._BuildWindows()
            self.buf._dirty = True

    # ── Input dispatch ────────────────────────────────────────────────────────

    def _OnEnter(self):
        """Handle Enter key: echo input, route it."""
        userInput = self.inputStr.strip()
        self.inputStr = ""
        if not userInput:
            return
        if self.busy:
            self.Writeln("  (AI is busy — please wait...)", C_YELLOW)
            return
        self.Writeln(f"\n>>> {userInput}", C_CYAN)
        self.logger.Log("INFO", f"User input [{gameState['mode']}]: {userInput}")
        self._RouteInput(userInput)

    def _RouteInput(self, text):
        """Dispatch input to the correct handler."""
        lower = text.lower().strip()

        if lower in ("menu", "back", "exit game", "games", "q"):
            self._ResetToMenu()
        elif lower == "help":
            self._ShowHelp()
        elif lower == "score":
            self._ShowScore()
        elif lower in ("1", "play number game", "number", "guessing"):
            self._StartNumberGame()
        elif lower in ("2", "play riddle game", "riddle", "quiz"):
            self._StartRiddleGame()
        elif gameState["mode"] == "number":
            self._HandleNumberInput(text)
        elif gameState["mode"] == "riddle":
            self._HandleRiddleAnswer(text)
        else:
            self._AskAI(text)

    # ── Welcome / Menu ────────────────────────────────────────────────────────

    def _ShowWelcome(self):
        """ASCII banner + game menu."""
        self.Writeln(r"  ___  _   _____ ___ ____  __  __ ___ _   _   _   _  ", C_CYAN)
        self.Writeln(r" / _ \| | |_   _/ _ \_  _||  \/  |_ _| \ | | /_\ | | ", C_CYAN)
        self.Writeln(r"| (_) | |__ | || (_) || |  | |\/| || ||  \| |/ _ \| |__", C_CYAN)
        self.Writeln(r" \___/|____|_|  \___/ |_|  |_|  |_|___|_|\__|_/ \_|____|", C_CYAN)
        self.Writeln("  AI Terminal  |  Ollama  |  Raspberry Pi", C_WHITE)
        self.Writeln(f"  Logs: {CONFIG['logDir']}/log-{datetime.now().strftime('%Y-%m-%d')}.log", C_DIM)
        self.Writeln()
        self._DrawMenu()

    def _DrawMenu(self):
        """Render the game-selector menu."""
        gameState["mode"] = "menu"
        self.Writeln("+---------------------------------+", C_YELLOW)
        self.Writeln("|        GAME  SELECTOR           |", C_YELLOW)
        self.Writeln("+---------------------------------+", C_YELLOW)
        self.Writeln("|  [1]  Number Guessing Game      |", C_WHITE)
        self.Writeln("|  [2]  Riddle Quiz               |", C_WHITE)
        self.Writeln("|  [?]  Ask the AI anything       |", C_WHITE)
        self.Writeln("+---------------------------------+", C_YELLOW)
        self.Writeln()
        self.Writeln("Type 1, 2, a command, or any question.", C_DIM)
        self.Writeln("Tip: type 'help' for all commands.", C_DIM)
        self.Writeln()

    def _ResetToMenu(self):
        """Clear game state, clear screen, redraw menu."""
        self.logger.Log("INFO", "Returning to menu")
        gameState.update({
            "mode": "menu", "secretNumber": None,
            "attempts": 0, "wrongAnswers": 0,
            "riddleAnswer": None, "riddleHint": None,
            "riddleActive": False, "hintGiven": False,
            "numberLow": 1, "numberHigh": 100,
        })
        self.ClearBuf()
        self._DrawMenu()

    def _ShowHelp(self):
        """Print command reference."""
        self.Writeln()
        self.Writeln("-- HELP -----------------------------------------", C_YELLOW)
        self.Writeln("  1 / play number game  -> Number Guessing Game", C_WHITE)
        self.Writeln("  2 / play riddle game  -> Riddle Quiz", C_WHITE)
        self.Writeln("  hint                  -> Get a hint (costs 1 hint token)", C_WHITE)
        self.Writeln("  skip                  -> (riddle) Skip to next riddle", C_WHITE)
        self.Writeln("  score                 -> Show session score", C_WHITE)
        self.Writeln("  menu                  -> Return to game selector", C_WHITE)
        self.Writeln("  help                  -> This screen", C_WHITE)
        self.Writeln("  <anything>            -> Ask the AI a question", C_WHITE)
        self.Writeln("  Ctrl+C                -> Quit", C_WHITE)
        self.Writeln("-------------------------------------------------", C_YELLOW)
        self.Writeln()

    def _ShowScore(self):
        """Display session score summary."""
        s = sessionScore
        self.Writeln()
        self.Writeln("-- SESSION SCORE --------------------------------", C_YELLOW)
        self.Writeln(f"  Number game wins : {s['numberWins']}", C_WHITE)
        bestStr = str(s['numberBest']) + " attempts" if s['numberBest'] else "N/A"
        self.Writeln(f"  Best number game : {bestStr}", C_WHITE)
        self.Writeln(f"  Riddle wins      : {s['riddleWins']}", C_WHITE)
        self.Writeln(f"  Best streak      : {s['riddleBest']}", C_WHITE)
        self.Writeln(f"  Current streak   : {s['riddleStreak']}", C_MAGENTA)
        self.Writeln(f"  Hints used       : {s['hintsUsed']}", C_DIM)
        self.Writeln("-------------------------------------------------", C_YELLOW)
        self.Writeln()
        self.logger.Log("INFO", f"Score shown: {s}")

    # ── General AI chat ───────────────────────────────────────────────────────

    def _AskAI(self, userInput):
        """Stream a free-form question to Ollama."""
        self.busy = True
        systemP = (
            "You are a helpful terminal assistant on a Raspberry Pi. "
            "Keep answers concise and plain-text — no markdown."
        )

        def _Run():
            self.Write("AI > ", C_CYAN)
            StreamOllama(userInput, lambda t: self.Write(t), systemP, self.logger)
            self.Writeln("\n")
            self.busy = False

        threading.Thread(target=_Run, daemon=True).start()

    # ──────────────────────────────────────────────────────────────────────────
    # GAME 1 — NUMBER GUESSING
    # ──────────────────────────────────────────────────────────────────────────

    def _StartNumberGame(self):
        """Initialise the number guessing game."""
        secret = random.randint(1, 100)
        gameState.update({
            "mode":         "number",
            "secretNumber": secret,
            "attempts":     0,
            "numberLow":    1,
            "numberHigh":   100,
            "hintGiven":    False,
        })
        self.logger.Log("INFO", f"Number game started — secret={secret}")
        self.Writeln()
        self.Writeln("+==============================================+", C_CYAN)
        self.Writeln("|         NUMBER  GUESSING  GAME              |", C_CYAN)
        self.Writeln("+==============================================+", C_CYAN)
        self.Writeln()
        self.Writeln("I'm thinking of a number between 1 and 100.", C_WHITE)
        self.Writeln("Type a number to guess, 'hint' for a clue, or 'menu' to quit.", C_DIM)
        self.Writeln()
        self.busy = True

        def _Intro():
            self.Write("AI > ", C_CYAN)
            StreamOllama(
                "You are a mysterious game host. Give one dramatic, teasing sentence "
                "daring the player to guess your secret number between 1 and 100. "
                "Max 25 words. Plain text only.",
                lambda t: self.Write(t),
                logger=self.logger,
            )
            self.Writeln("\n")
            self.busy = False

        threading.Thread(target=_Intro, daemon=True).start()

    def _HandleNumberInput(self, text):
        """Route number-game input: hint request or a numeric guess."""
        if text.lower() == "hint":
            self._GiveNumberHint()
        else:
            self._HandleNumberGuess(text)

    def _GiveNumberHint(self):
        """Reveal the current narrowed range as a hint, then ask AI for flavour."""
        sessionScore["hintsUsed"] += 1
        gameState["hintGiven"] = True
        low  = gameState["numberLow"]
        high = gameState["numberHigh"]
        self.Writeln(f"  [HINT] The number is between {low} and {high}.", C_YELLOW)
        self.logger.Log("INFO", f"Number hint given: {low}-{high}")
        self.busy = True

        def _HintFlavour():
            self.Write("AI > ", C_CYAN)
            StreamOllama(
                f"The player asked for a hint. Tell them dramatically that the secret "
                f"number is somewhere between {low} and {high}. "
                "Max 20 words. Plain text only.",
                lambda t: self.Write(t),
                logger=self.logger,
            )
            self.Writeln("\n")
            self.busy = False

        threading.Thread(target=_HintFlavour, daemon=True).start()

    def _HandleNumberGuess(self, text):
        """Validate and evaluate a numeric guess with AI commentary."""
        try:
            guess = int(text)
        except ValueError:
            self.Writeln("  Please enter a whole number (or 'hint').", C_YELLOW)
            return

        gameState["attempts"] += 1
        secret   = gameState["secretNumber"]
        attempts = gameState["attempts"]

        # Narrowing the known range for the hint system
        if guess < secret:
            gameState["numberLow"] = max(gameState["numberLow"], guess + 1)
        elif guess > secret:
            gameState["numberHigh"] = min(gameState["numberHigh"], guess - 1)

        # How close is the guess? (for hot/cold commentary)
        diff = abs(guess - secret)
        if diff == 0:
            temperature = "correct"
        elif diff <= 3:
            temperature = "BURNING HOT"
        elif diff <= 10:
            temperature = "warm"
        elif diff <= 25:
            temperature = "cold"
        else:
            temperature = "FREEZING"

        self.logger.Log("INFO",
            f"Number guess: {guess} | secret: {secret} | diff: {diff} | attempts: {attempts}")

        if guess < secret:
            self.Writeln(f"  ^ Too low!  [{temperature}]  (attempt {attempts})", C_YELLOW)
            self._NumberCommentary("low", guess, secret, temperature, attempts)
        elif guess > secret:
            self.Writeln(f"  v Too high! [{temperature}]  (attempt {attempts})", C_YELLOW)
            self._NumberCommentary("high", guess, secret, temperature, attempts)
        else:
            self._NumberWin(secret, attempts)

    def _NumberCommentary(self, direction, guess, secret, temperature, attempts):
        """
        Stream a short AI comment after each wrong guess.

        Args:
            direction  : "low" or "high"
            guess      : The player's guess.
            secret     : The actual secret number.
            temperature: Hot/cold string description.
            attempts   : Number of attempts so far.
        """
        self.busy = True

        def _Run():
            prompt = (
                f"The player guessed {guess}, which is too {direction}. "
                f"The temperature is '{temperature}'. "
                f"This is attempt number {attempts}. "
                "Give ONE short, witty, dramatic reaction. "
                "Max 18 words. Plain text only. No emojis."
            )
            self.Write("AI > ", C_CYAN)
            StreamOllama(prompt, lambda t: self.Write(t), logger=self.logger)
            self.Writeln("\n")
            self.busy = False

        threading.Thread(target=_Run, daemon=True).start()

    def _NumberWin(self, secret, attempts):
        """Handle a correct number guess: update score and stream win message."""
        # Update session score
        sessionScore["numberWins"] += 1
        if sessionScore["numberBest"] is None or attempts < sessionScore["numberBest"]:
            sessionScore["numberBest"] = attempts
            newRecord = True
        else:
            newRecord = False

        self.logger.Log("INFO",
            f"Number game WON in {attempts} attempts. New record: {newRecord}")

        rating = "genius" if attempts <= 5 else "great" if attempts <= 10 else "ok"

        self.Writeln()
        self.Writeln(f"  [WIN!] The number was {secret}!", C_NORMAL)
        self.Writeln(f"  You got it in {attempts} attempt{'s' if attempts != 1 else ''}.", C_WHITE)
        if newRecord:
            self.Writeln("  ** NEW PERSONAL BEST! **", C_MAGENTA)
        self.Writeln()
        self.busy = True

        def _Win():
            prompt = (
                f"The player just won! They guessed {secret} in {attempts} attempts. "
                f"Performance rating: {rating}. "
                + ("This is a new personal best! " if newRecord else "")
                + "Give a SHORT dramatic congratulation (or gentle taunt if it took many attempts). "
                "Max 25 words. Plain text only."
            )
            self.Write("AI > ", C_CYAN)
            StreamOllama(prompt, lambda t: self.Write(t), logger=self.logger)
            self.Writeln("\n")
            self.busy = False
            time.sleep(2)
            self._ResetToMenu()

        threading.Thread(target=_Win, daemon=True).start()

    # ──────────────────────────────────────────────────────────────────────────
    # GAME 2 — RIDDLE QUIZ
    # ──────────────────────────────────────────────────────────────────────────

    def _StartRiddleGame(self):
        """Initialise the riddle quiz and fetch the first riddle."""
        gameState.update({
            "mode":         "riddle",
            "riddleActive": False,
            "riddleAnswer": None,
            "riddleHint":   None,
            "wrongAnswers": 0,
            "hintGiven":    False,
        })
        self.logger.Log("INFO", "Riddle game started")
        self.Writeln()
        self.Writeln("+==============================================+", C_CYAN)
        self.Writeln("|               RIDDLE  QUIZ                  |", C_CYAN)
        self.Writeln("+==============================================+", C_CYAN)
        self.Writeln()
        self.Writeln("Solve the riddles. After 3 wrong answers type 'hint'.", C_DIM)
        self.Writeln("'skip' for next riddle  |  'menu' to quit", C_DIM)
        self.Writeln()
        self._FetchRiddle()

    def _FetchRiddle(self):
        """Ask the LLM to generate a riddle + hint; parse the JSON response."""
        self.busy = True
        gameState["riddleActive"] = False
        gameState["riddleAnswer"] = None
        gameState["riddleHint"]   = None
        gameState["wrongAnswers"] = 0
        gameState["hintGiven"]    = False
        self.Writeln("  ... generating riddle ...", C_DIM)

        def _Run():
            systemP = (
                "You generate riddles. Respond ONLY with a single JSON object:\n"
                '{"riddle":"<question>","answer":"<one word or short phrase>","hint":"<subtle clue, not the answer>"}\n'
                "No markdown. No extra text. Just the JSON."
            )
            parts = []
            StreamOllama(
                "Give me a clever but solvable riddle.",
                lambda t: parts.append(t),
                systemP,
                self.logger,
            )
            raw = "".join(parts).strip().replace("```json", "").replace("```", "").strip()

            # Robustly extract JSON even if the model leaks extra text
            try:
                start  = raw.index("{")
                end    = raw.rindex("}") + 1
                data   = json.loads(raw[start:end])
                riddle = data.get("riddle", "").strip()
                answer = data.get("answer", "").strip().lower()
                hint   = data.get("hint", "Think carefully...").strip()
                if not riddle or not answer:
                    raise ValueError("Empty fields")
            except (ValueError, json.JSONDecodeError, KeyError):
                riddle = "I have hands but cannot clap. What am I?"
                answer = "clock"
                hint   = "You use it to tell time."

            gameState["riddleAnswer"] = answer
            gameState["riddleHint"]   = hint
            gameState["riddleActive"] = True

            self.logger.Log("INFO", f"Riddle fetched — answer: {answer}")

            self.Writeln()
            self.Writeln("  [RIDDLE]", C_YELLOW)
            self.Writeln(f"  {riddle}", C_WHITE)
            self.Writeln()
            self.Writeln("  Your answer (type 'hint' after 3 wrong guesses):", C_DIM)
            self.busy = False

        threading.Thread(target=_Run, daemon=True).start()

    def _HandleRiddleAnswer(self, text):
        """Evaluate the player's riddle answer; handle hints and skips."""
        lower = text.lower().strip()

        if lower == "skip":
            self.Writeln("  Skipping this riddle...", C_DIM)
            sessionScore["riddleStreak"] = 0   # streak broken on skip
            self.logger.Log("INFO", "Riddle skipped")
            self._FetchRiddle()
            return

        if lower == "hint":
            self._GiveRiddleHint()
            return

        if not gameState["riddleActive"] or not gameState["riddleAnswer"]:
            self.Writeln("  Riddle not ready yet — please wait.", C_YELLOW)
            return

        playerAnswer  = lower
        correctAnswer = gameState["riddleAnswer"]

        # Flexible match: either string is a substring of the other
        isCorrect = (correctAnswer in playerAnswer or playerAnswer in correctAnswer)

        self.logger.Log("INFO",
            f"Riddle answer: '{text}' | correct: '{correctAnswer}' | match: {isCorrect}")

        if isCorrect:
            self._RiddleCorrect(correctAnswer)
        else:
            self._RiddleWrong(text)

    def _GiveRiddleHint(self):
        """
        Reveal the pre-fetched hint.
        Only available after 3 wrong answers or via the 'hint' command.
        """
        wrongCount = gameState["wrongAnswers"]
        if wrongCount < 3 and not gameState["hintGiven"]:
            self.Writeln(
                f"  You need at least 3 wrong answers before a hint. "
                f"You have {wrongCount} so far.", C_YELLOW)
            return

        if gameState["hintGiven"]:
            self.Writeln("  Hint already given! Keep thinking.", C_DIM)
            return

        if not gameState["riddleHint"]:
            self.Writeln("  No hint available for this riddle.", C_DIM)
            return

        gameState["hintGiven"] = True
        sessionScore["hintsUsed"] += 1
        self.Writeln(f"  [HINT] {gameState['riddleHint']}", C_YELLOW)
        self.logger.Log("INFO", f"Riddle hint given: {gameState['riddleHint']}")

    def _RiddleWrong(self, text):
        """Handle an incorrect riddle answer with AI commentary."""
        gameState["wrongAnswers"] += 1
        wrongCount = gameState["wrongAnswers"]
        sessionScore["riddleStreak"] = 0    # streak broken on wrong answer

        self.Writeln(f"  [WRONG] '{text}' is not right. "
                     f"(attempt {wrongCount})", C_RED)

        if wrongCount == 3:
            self.Writeln("  Tip: type 'hint' to get a clue!", C_YELLOW)

        self.busy = True

        def _Run():
            prompt = (
                f"The player guessed '{text}' for a riddle but it's wrong. "
                f"This is their attempt number {wrongCount}. "
                + ("They've been trying hard — maybe encourage them a little. " if wrongCount >= 3 else "")
                + "Give ONE short, witty, teasing response. Max 18 words. Plain text only."
            )
            self.Write("AI > ", C_CYAN)
            StreamOllama(prompt, lambda t: self.Write(t), logger=self.logger)
            self.Writeln("\n")
            self.busy = False

        threading.Thread(target=_Run, daemon=True).start()

    def _RiddleCorrect(self, correctAnswer):
        """Handle a correct riddle answer: update streak and stream praise."""
        sessionScore["riddleWins"] += 1
        sessionScore["riddleStreak"] += 1
        currentStreak = sessionScore["riddleStreak"]
        if currentStreak > sessionScore["riddleBest"]:
            sessionScore["riddleBest"] = currentStreak

        isNewStreakRecord = currentStreak == sessionScore["riddleBest"] and currentStreak > 1
        self.logger.Log("INFO",
            f"Riddle correct! answer={correctAnswer} streak={currentStreak}")

        self.Writeln(f"\n  [CORRECT!] The answer was '{correctAnswer}'.", C_NORMAL)
        if currentStreak > 1:
            tag = C_MAGENTA if currentStreak >= 3 else C_WHITE
            self.Writeln(f"  STREAK: {currentStreak} in a row!", tag)
        if isNewStreakRecord:
            self.Writeln(f"  ** NEW STREAK RECORD: {currentStreak}! **", C_MAGENTA)
        self.Writeln()
        self.busy = True

        def _Next():
            prompt = (
                f"The player correctly answered '{correctAnswer}' to a riddle. "
                f"They are on a streak of {currentStreak} correct answers. "
                + ("This is their personal best streak! " if isNewStreakRecord else "")
                + "Give ONE short excited congratulation. Max 20 words. Plain text only."
            )
            self.Write("AI > ", C_CYAN)
            StreamOllama(prompt, lambda t: self.Write(t), logger=self.logger)
            self.Writeln("\n")
            self.busy = False
            time.sleep(0.8)
            self._FetchRiddle()

        threading.Thread(target=_Next, daemon=True).start()


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    """Entry point — wraps curses so the terminal always restores on exit."""
    try:
        curses.wrapper(lambda stdscr: TerminalApp(stdscr))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
