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
# GAMES:
#   1. Number Guessing  – guess the secret number between 1 and 100
#   2. Riddle Quiz      – solve AI-generated riddles
#
# COMMANDS (type in the input box):
#   1 / play number game   → Number Guessing Game
#   2 / play riddle game   → Riddle Quiz
#   menu / back            → Return to game selector
#   help                   → Show available commands
#   skip                   → (Riddle mode) next riddle
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

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
CONFIG = {
    "ollamaHost": "http://localhost:11434",
    # "model":      "gemma2:2b",
    "model":      "llama3.2",
    # MODEL_NAME = "llama3.2:1b"                   # model name pulled in Ollama
    # MODEL_NAME = "llama3.2"                   # model name pulled in Ollama
    # MODEL_NAME = "llama2-uncensored:7b"                   # model name pulled in Ollama
    "streamDelay": 0.02,          # seconds between token paints
    "maxLines":   500,            # scroll-back buffer size
}

# ──────────────────────────────────────────────────────────────────────────────
# COLOUR PAIR IDs
# ──────────────────────────────────────────────────────────────────────────────
C_NORMAL  = 1   # green on black  — default text
C_CYAN    = 2   # cyan on black   — prompts / headers
C_YELLOW  = 3   # yellow on black — warnings / boxes
C_RED     = 4   # red on black    — errors
C_WHITE   = 5   # white on black  — body text
C_DIM     = 6   # dark grey       — hints
C_INPUT   = 7   # black on green  — input bar
C_STATUS  = 8   # black on cyan   — status bar

# ──────────────────────────────────────────────────────────────────────────────
# GAME STATE
# ──────────────────────────────────────────────────────────────────────────────
gameState = {
    "mode":         "menu",   # "menu" | "number" | "riddle"
    "secretNumber": None,
    "riddleAnswer": None,
    "riddleActive": False,
    "attempts":     0,
}


# ──────────────────────────────────────────────────────────────────────────────
# OLLAMA HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def StreamOllama(prompt, onToken, systemPrompt=None):
    """
    Stream tokens from the local Ollama /api/generate endpoint.

    Args:
        prompt      : User prompt string.
        onToken     : Callable(token: str) — invoked for every streamed token.
        systemPrompt: Optional system prompt string.
    """
    payload = {"model": CONFIG["model"], "prompt": prompt, "stream": True}
    if systemPrompt:
        payload["system"] = systemPrompt

    try:
        with requests.post(
            f"{CONFIG['ollamaHost']}/api/generate",
            json=payload, stream=True, timeout=120,
        ) as resp:
            resp.raise_for_status()
            for rawLine in resp.iter_lines():
                if rawLine:
                    try:
                        chunk = json.loads(rawLine)
                        token = chunk.get("response", "")
                        if token:
                            onToken(token)
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        pass
    except requests.exceptions.ConnectionError:
        onToken("\n[ERROR] Cannot connect to Ollama — run: ollama serve\n")
    except requests.exceptions.Timeout:
        onToken("\n[ERROR] Ollama request timed out.\n")
    except Exception as exc:
        onToken(f"\n[ERROR] {exc}\n")


# ──────────────────────────────────────────────────────────────────────────────
# SCROLL BUFFER
# ──────────────────────────────────────────────────────────────────────────────

class ScrollBuffer:
    """Thread-safe line buffer that the curses renderer reads from."""

    def __init__(self, maxLines=500):
        self._lines    = []          # list of (str, colorId)
        self._lock     = threading.Lock()
        self._maxLines = maxLines
        self._dirty    = True

    def Append(self, text, colorId=C_NORMAL):
        """
        Append text to the buffer, streaming tokens into the current line
        when the colour matches and no newline has ended it yet.

        Args:
            text    : String (may contain newlines).
            colorId : Curses colour-pair ID.
        """
        with self._lock:
            if (self._lines
                    and self._lines[-1][1] == colorId
                    and not self._lines[-1][0].endswith("\n")):
                combined = self._lines[-1][0] + text
                self._lines[-1] = (combined, colorId)
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
        """Return a snapshot copy."""
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
      [0]        status bar
      [1..H-3]   scroll area
      [H-2]      mode bar
      [H-1]      input bar
    """

    def __init__(self, stdscr):
        """Initialise curses, build windows, show welcome, start event loop."""
        self.stdscr   = stdscr
        self.buf      = ScrollBuffer(CONFIG["maxLines"])
        self.inputStr = ""
        self.busy     = False
        self.running  = True

        self._InitCurses()
        self._BuildWindows()
        self._ShowWelcome()
        self._Loop()

    # ── Curses setup ──────────────────────────────────────────────────────────

    def _InitCurses(self):
        """Configure colours, cursor, and non-blocking input."""
        curses.curs_set(1)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)

        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(C_NORMAL, curses.COLOR_GREEN,  -1)
        curses.init_pair(C_CYAN,   curses.COLOR_CYAN,   -1)
        curses.init_pair(C_YELLOW, curses.COLOR_YELLOW, -1)
        curses.init_pair(C_RED,    curses.COLOR_RED,    -1)
        curses.init_pair(C_WHITE,  curses.COLOR_WHITE,  -1)
        curses.init_pair(C_DIM,    8,                   -1)  # dark grey (colour 8)
        curses.init_pair(C_INPUT,  curses.COLOR_BLACK,  curses.COLOR_GREEN)
        curses.init_pair(C_STATUS, curses.COLOR_BLACK,  curses.COLOR_CYAN)

    def _BuildWindows(self):
        """Create sub-windows sized to current terminal dimensions."""
        self.H, self.W = self.stdscr.getmaxyx()
        self.scrollH   = max(1, self.H - 3)

        self.scrollWin = curses.newwin(self.scrollH, self.W, 1, 0)
        self.scrollWin.scrollok(True)

        self.statusWin = curses.newwin(1, self.W, 0, 0)
        self.modeWin   = curses.newwin(1, self.W, self.H - 2, 0)
        self.inputWin  = curses.newwin(1, self.W, self.H - 1, 0)

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _Render(self):
        """Redraw all four UI regions."""
        self._DrawStatusBar()
        self._DrawScrollArea()
        self._DrawModeBar()
        self._DrawInputBar()

    def _DrawStatusBar(self):
        text = (
            f" AI TERMINAL  |  model: {CONFIG['model']}"
            f"  |  {CONFIG['ollamaHost']} "
        )
        self.statusWin.erase()
        self.statusWin.bkgd(" ", curses.color_pair(C_STATUS))
        try:
            self.statusWin.addnstr(0, 0, text.ljust(self.W), self.W,
                                   curses.color_pair(C_STATUS) | curses.A_BOLD)
        except curses.error:
            pass
        self.statusWin.noutrefresh()

    def _DrawModeBar(self):
        text = f"  MODE: {gameState['mode'].upper()}   |  Ctrl+C to quit"
        self.modeWin.erase()
        self.modeWin.bkgd(" ", curses.color_pair(C_INPUT))
        try:
            self.modeWin.addnstr(0, 0, text.ljust(self.W), self.W,
                                 curses.color_pair(C_INPUT))
        except curses.error:
            pass
        self.modeWin.noutrefresh()

    def _DrawScrollArea(self):
        """Word-wrap buffer entries and display the last scrollH lines."""
        self.scrollWin.erase()
        self.scrollWin.bkgd(" ", curses.color_pair(C_NORMAL))

        displayLines = []
        for rawText, colorId in self.buf.GetLines():
            for segment in rawText.split("\n"):
                if segment == "":
                    displayLines.append(("", colorId))
                else:
                    wrapped = textwrap.wrap(segment, self.W - 1) or [""]
                    for wLine in wrapped:
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
        """Draw the prompt arrow and current input string."""
        prefix  = ">>> " if not self.busy else "... "
        display = (prefix + self.inputStr)[-(self.W - 1):]
        self.inputWin.erase()
        self.inputWin.bkgd(" ", curses.color_pair(C_NORMAL))
        try:
            self.inputWin.addnstr(0, 0, display.ljust(self.W - 1),
                                  self.W - 1, curses.color_pair(C_NORMAL) | curses.A_BOLD)
            self.inputWin.move(0, min(len(display), self.W - 2))
        except curses.error:
            pass
        self.inputWin.noutrefresh()

    # ── Write helpers (safe from any thread) ─────────────────────────────────

    def Write(self, text, colorId=C_NORMAL):
        """Append text to the scroll buffer."""
        self.buf.Append(text, colorId)

    def Writeln(self, text="", colorId=C_NORMAL):
        """Append text + newline to the scroll buffer."""
        self.buf.Append(text + "\n", colorId)

    def ClearBuf(self):
        """Clear the scroll buffer."""
        self.buf.Clear()

    # ── Event loop ────────────────────────────────────────────────────────────

    def _Loop(self):
        """
        Non-blocking event loop (~60 fps).
        Redraws only when the buffer is dirty or the input string changed.
        """
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
            elif ch == 3:                          # Ctrl+C
                self.running = False
            elif 32 <= ch <= 126:                  # Printable ASCII
                self.inputStr += chr(ch)

    def _HandleResize(self):
        """Rebuild sub-windows when the terminal is resized."""
        newH, newW = self.stdscr.getmaxyx()
        if newH != self.H or newW != self.W:
            self.H, self.W = newH, newW
            curses.resizeterm(newH, newW)
            self._BuildWindows()
            self.buf._dirty = True

    # ── Input routing ─────────────────────────────────────────────────────────

    def _OnEnter(self):
        """Handle the Enter key — echo input then route it."""
        userInput = self.inputStr.strip()
        self.inputStr = ""
        if not userInput:
            return
        if self.busy:
            self.Writeln("  (please wait — AI is busy...)", C_YELLOW)
            return
        self.Writeln(f"\n>>> {userInput}", C_CYAN)
        self._RouteInput(userInput)

    def _RouteInput(self, text):
        """Dispatch to game handler or AI chat based on mode and keywords."""
        lower = text.lower()

        if lower in ("menu", "back", "exit game", "show games", "games", "q"):
            self._ResetToMenu()
            return
        if lower == "help":
            self._ShowHelp()
            return
        if lower in ("1", "play number game", "number", "guessing"):
            self._StartNumberGame()
            return
        if lower in ("2", "play riddle game", "riddle", "quiz"):
            self._StartRiddleGame()
            return

        if gameState["mode"] == "number":
            self._HandleNumberGuess(text)
        elif gameState["mode"] == "riddle":
            self._HandleRiddleAnswer(text)
        else:
            self._AskAI(text)

    # ── Welcome / Menu ────────────────────────────────────────────────────────

    def _ShowWelcome(self):
        """Print ASCII banner then the game menu."""
        self.Writeln(r"  ___  _   _____ ___ ____  __  __ ___ _   _   _   _  ", C_CYAN)
        self.Writeln(r" / _ \| | |_   _/ _ \_  _||  \/  |_ _| \ | | /_\ | | ", C_CYAN)
        self.Writeln(r"| (_) | |__ | || (_) || |  | |\/| || ||  \| |/ _ \| |__", C_CYAN)
        self.Writeln(r" \___/|____|_|  \___/ |_|  |_|  |_|___|_|\__|_/ \_|____|", C_CYAN)
        self.Writeln("  AI Terminal  |  Ollama  |  Raspberry Pi", C_WHITE)
        self.Writeln()
        self._DrawMenu()

    def _DrawMenu(self):
        """Render the game selector."""
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
        self.Writeln("Commands: 1 | 2 | menu | help | Ctrl+C to quit", C_DIM)
        self.Writeln()

    def _ResetToMenu(self):
        """Clear state and redraw the menu."""
        gameState.update({
            "mode": "menu", "secretNumber": None,
            "riddleAnswer": None, "riddleActive": False, "attempts": 0,
        })
        self.ClearBuf()
        self._DrawMenu()

    def _ShowHelp(self):
        """Print the help screen."""
        self.Writeln()
        self.Writeln("-- HELP ---------------------------------", C_YELLOW)
        self.Writeln("  1 / play number game  -> Number Guessing", C_WHITE)
        self.Writeln("  2 / play riddle game  -> Riddle Quiz", C_WHITE)
        self.Writeln("  menu                  -> Game selector", C_WHITE)
        self.Writeln("  skip     (riddle mode)-> Next riddle", C_WHITE)
        self.Writeln("  help                  -> This screen", C_WHITE)
        self.Writeln("  <anything>            -> Ask the AI", C_WHITE)
        self.Writeln("  Ctrl+C                -> Quit", C_WHITE)
        self.Writeln("-----------------------------------------", C_YELLOW)
        self.Writeln()

    # ── General AI chat ───────────────────────────────────────────────────────

    def _AskAI(self, userInput):
        """Stream a free-form question to Ollama and display the response."""
        self.busy = True
        systemP = (
            "You are a helpful terminal assistant on a Raspberry Pi. "
            "Keep answers concise. Plain text only, no markdown."
        )

        def _Run():
            self.Write("AI > ", C_CYAN)
            StreamOllama(userInput, lambda t: self.Write(t), systemP)
            self.Writeln("\n")
            self.busy = False

        threading.Thread(target=_Run, daemon=True).start()

    # ──────────────────────────────────────────────────────────────────────────
    # GAME 1: NUMBER GUESSING
    # ──────────────────────────────────────────────────────────────────────────

    def _StartNumberGame(self):
        """Initialise the number guessing game with a random secret number."""
        gameState.update({
            "mode": "number",
            "secretNumber": random.randint(1, 100),
            "attempts": 0,
        })
        self.Writeln()
        self.Writeln("+==============================================+", C_CYAN)
        self.Writeln("|         NUMBER  GUESSING  GAME              |", C_CYAN)
        self.Writeln("+==============================================+", C_CYAN)
        self.Writeln()
        self.Writeln("I'm thinking of a number between 1 and 100.", C_WHITE)
        self.Writeln("Type your guess. Type 'menu' to quit.", C_DIM)
        self.Writeln()
        self.busy = True

        def _Intro():
            self.Write("AI > ", C_CYAN)
            StreamOllama(
                "One dramatic short sentence daring the player to guess your secret "
                "number between 1 and 100. Max 20 words. Plain text only.",
                lambda t: self.Write(t),
            )
            self.Writeln("\n")
            self.busy = False

        threading.Thread(target=_Intro, daemon=True).start()

    def _HandleNumberGuess(self, text):
        """
        Validate input and compare guess to the secret number.

        Args:
            text: Raw input string from the player.
        """
        try:
            guess = int(text)
        except ValueError:
            self.Writeln("Please enter a whole number.", C_YELLOW)
            return

        gameState["attempts"] += 1
        secret   = gameState["secretNumber"]
        attempts = gameState["attempts"]

        if guess < secret:
            self.Writeln(f"  ^ Too low!   (attempt {attempts})", C_YELLOW)
        elif guess > secret:
            self.Writeln(f"  v Too high!  (attempt {attempts})", C_YELLOW)
        else:
            self.Writeln(
                f"\n  [WIN] Correct! The number was {secret}. "
                f"You got it in {attempts} attempt{'s' if attempts != 1 else ''}!\n",
                C_NORMAL,
            )
            self.busy = True

            def _Win():
                prompt = (
                    f"The player guessed {secret} in {attempts} attempt(s). "
                    "One short congratulation or taunt. Max 20 words. Plain text."
                )
                self.Write("AI > ", C_CYAN)
                StreamOllama(prompt, lambda t: self.Write(t))
                self.Writeln("\n")
                self.busy = False
                time.sleep(1.5)
                self._ResetToMenu()

            threading.Thread(target=_Win, daemon=True).start()

    # ──────────────────────────────────────────────────────────────────────────
    # GAME 2: RIDDLE QUIZ
    # ──────────────────────────────────────────────────────────────────────────

    def _StartRiddleGame(self):
        """Initialise the riddle quiz."""
        gameState.update({
            "mode": "riddle",
            "riddleActive": False,
            "riddleAnswer": None,
        })
        self.Writeln()
        self.Writeln("+==============================================+", C_CYAN)
        self.Writeln("|               RIDDLE  QUIZ                  |", C_CYAN)
        self.Writeln("+==============================================+", C_CYAN)
        self.Writeln()
        self.Writeln("Solve the AI's riddle. 'skip' for next. 'menu' to quit.", C_DIM)
        self.Writeln()
        self._FetchRiddle()

    def _FetchRiddle(self):
        """Ask the LLM to generate a riddle and parse the JSON response."""
        self.busy = True
        gameState["riddleActive"] = False
        gameState["riddleAnswer"] = None
        self.Writeln("  ... generating riddle ...", C_DIM)

        def _Run():
            systemP = (
                "You generate riddles. Respond ONLY with a single JSON object:\n"
                '{"riddle":"<question>","answer":"<one word or short phrase>"}\n'
                "No markdown. No explanation. No extra text whatsoever."
            )
            parts = []
            StreamOllama("Give me a simple riddle.", lambda t: parts.append(t), systemP)
            raw = "".join(parts).strip().replace("```json", "").replace("```", "").strip()

            # Extract JSON robustly even if the model adds stray text
            try:
                start  = raw.index("{")
                end    = raw.rindex("}") + 1
                data   = json.loads(raw[start:end])
                riddle = data.get("riddle", "").strip()
                answer = data.get("answer", "").strip().lower()
                if not riddle or not answer:
                    raise ValueError("Empty fields")
            except (ValueError, json.JSONDecodeError, KeyError):
                riddle = "I have hands but cannot clap. What am I?"
                answer = "clock"

            gameState["riddleAnswer"] = answer
            gameState["riddleActive"] = True

            self.Writeln()
            self.Writeln("  [RIDDLE]", C_YELLOW)
            self.Writeln(f"  {riddle}", C_WHITE)
            self.Writeln()
            self.Writeln("  Your answer:", C_DIM)
            self.busy = False

        threading.Thread(target=_Run, daemon=True).start()

    def _HandleRiddleAnswer(self, text):
        """
        Compare the player's answer to the stored riddle answer.

        Args:
            text: Raw input string from the player.
        """
        if text.lower() == "skip":
            self.Writeln("  Skipping...", C_DIM)
            self._FetchRiddle()
            return

        if not gameState["riddleActive"] or not gameState["riddleAnswer"]:
            self.Writeln("  Hold on — riddle not ready yet.", C_YELLOW)
            return

        playerAnswer  = text.strip().lower()
        correctAnswer = gameState["riddleAnswer"]

        # Flexible matching: either string contains the other
        if correctAnswer in playerAnswer or playerAnswer in correctAnswer:
            self.Writeln(f"\n  [CORRECT] The answer was '{correctAnswer}'.\n", C_NORMAL)
            self.busy = True

            def _Next():
                self.Write("AI > ", C_CYAN)
                StreamOllama(
                    "One short witty congratulation to the player. Max 15 words. Plain text.",
                    lambda t: self.Write(t),
                )
                self.Writeln("\n")
                self.busy = False
                time.sleep(0.8)
                self._FetchRiddle()

            threading.Thread(target=_Next, daemon=True).start()
        else:
            self.Writeln(f"  [WRONG] '{text}' is not right. Try again or type 'skip'.", C_RED)
            self.Writeln()


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    """Wrap curses.wrapper so the terminal is always restored on exit."""
    try:
        curses.wrapper(lambda stdscr: TerminalApp(stdscr))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
