#!/usr/bin/env python3
"""
main.py

Matrix keyboard firmware for Raspberry Pi 5 using HID gadget.
Features:
- 4x10 matrix scanning
- Layer 1 (short press + long press)
- Layer 2 (normal)
- Layer up / layer down keys
- Debug logs for clarity
"""

import time
import glob
from gpiozero import DigitalOutputDevice, Button
from hidpi import Keyboard
from hidpi.keyboard_keys import *

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

scanDelay = 0.02
longPressTime = 0.6  # seconds
maxHidKeys = 6

ROW_PINS_BCM = [26, 19, 13, 6]
COL_PINS_BCM = [21, 20, 16, 12, 1, 7, 8, 25, 24, 23]

# ---------------------------------------------------------------------
# Key Layers
# ---------------------------------------------------------------------

KEY_MATRIX_LAYER_01_PRESSED = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'SEMICOLON'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'COMMA', 'PERIOD', 'SLASH'],
    ['ESC', 'SPACE', 'LAYER_UP', '', '', 'LAYER_DOWN', 'ENTER', 'BACKSPACE', '', '']
]

KEY_MATRIX_LAYER_01_LONG_PRESSED = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
    ['LEFT_GUI', 'LEFT_ALT', 'LEFT_CTRL', 'LEFT_SHIFT', 'TAB', 'TAB',
     'RIGHT_SHIFT', 'RIGHT_CTRL', 'RIGHT_ALT', 'RIGHT_GUI'],
    ['LEFT_BRACKET', 'RIGHT_BRACKET', 'BACKSLASH', 'MINUS', 'EQUAL', '', '', '', '', ''],
    ['ESC', 'SPACE', 'LAYER_UP', '', '', 'LAYER_DOWN', 'ENTER', '', '', '']
]

KEY_MATRIX_LAYER_02 = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'SEMICOLON'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'COMMA', 'PERIOD', 'SLASH'],
    ['ESC', 'SPACE', 'LAYER_UP', '', '', 'LAYER_DOWN', 'ENTER', 'BACKSPACE', '', '']
]

# ---------------------------------------------------------------------
# Key Mapping
# ---------------------------------------------------------------------

keyMap = {
    'Q': KEY_Q, 'W': KEY_W, 'E': KEY_E, 'R': KEY_R, 'T': KEY_T,
    'Y': KEY_Y, 'U': KEY_U, 'I': KEY_I, 'O': KEY_O, 'P': KEY_P,
    'A': KEY_A, 'S': KEY_S, 'D': KEY_D, 'F': KEY_F, 'G': KEY_G,
    'H': KEY_H, 'J': KEY_J, 'K': KEY_K, 'L': KEY_L,
    'Z': KEY_Z, 'X': KEY_X, 'C': KEY_C, 'V': KEY_V, 'B': KEY_B,
    'N': KEY_N, 'M': KEY_M,
    '1': KEY_1, '2': KEY_2, '3': KEY_3, '4': KEY_4, '5': KEY_5,
    '6': KEY_6, '7': KEY_7, '8': KEY_8, '9': KEY_9, '0': KEY_0,
    'ESC': KEY_ESC, 'TAB': KEY_TAB, 'SPACE': KEY_SPACE,
    'ENTER': KEY_ENTER, 'BACKSPACE': KEY_BACKSPACE,
    'SEMICOLON': KEY_SEMICOLON, 'COMMA': KEY_COMMA,
    'PERIOD': KEY_PERIOD, 'SLASH': KEY_SLASH,
    'LEFT_SHIFT': KEY_LEFT_SHIFT, 'RIGHT_SHIFT': KEY_RIGHT_SHIFT,
    'LEFT_CTRL': KEY_LEFT_CTRL, 'RIGHT_CTRL': KEY_RIGHT_CTRL,
    'LEFT_ALT': KEY_LEFT_ALT, 'RIGHT_ALT': KEY_RIGHT_ALT,
    'LEFT_GUI': KEY_LEFT_GUI, 'RIGHT_GUI': KEY_RIGHT_GUI,
    'LEFT_BRACKET': KEY_LEFT_BRACKET, 'RIGHT_BRACKET': KEY_RIGHT_BRACKET,
    'BACKSLASH': KEY_BACKSLASH, 'MINUS': KEY_MINUS, 'EQUAL': KEY_EQUAL
}

# ---------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------

rowGpios = []
colGpios = []

matrixState = [[False] * 10 for _ in range(4)]
pressTime = [[0] * 10 for _ in range(4)]

currentLayer = 1

# ---------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------

def TestHid():
    """Validate HID gadget."""
    devices = glob.glob('/dev/hidg*')
    if not devices:
        raise RuntimeError("No HID gadget found")
    print(f"[INFO] HID device detected: {devices[0]}")

def SetupMatrixKeyboard():
    """Initialize GPIO pins."""
    try:
        print("[INFO] Initializing GPIO matrix...")
        for pin in ROW_PINS_BCM:
            rowGpios.append(DigitalOutputDevice(pin, initial_value=False))
        for pin in COL_PINS_BCM:
            colGpios.append(Button(pin, pull_up=False))
        print("[OK] GPIO matrix ready")
    except Exception as e:
        CleanupMatrixKeyboard()
        raise RuntimeError(f"GPIO init failed: {e}")

def ScanMatrix():
    """Scan matrix and return pressed keys."""
    pressed = []
    for r, row in enumerate(rowGpios):
        row.on()
        time.sleep(0.001)
        for c, col in enumerate(colGpios):
            if col.is_pressed:
                pressed.append((r, c))
        row.off()
    return pressed

def GetActiveKey(row, col, isLong):
    """Return key based on layer and press duration."""
    if currentLayer == 1:
        return (KEY_MATRIX_LAYER_01_LONG_PRESSED if isLong else
                KEY_MATRIX_LAYER_01_PRESSED)[row][col]
    return KEY_MATRIX_LAYER_02[row][col]

# ---------------------------------------------------------------------
# Core Logic
# ---------------------------------------------------------------------

def UpdateKeyboard():
    """Update HID state from matrix."""
    global currentLayer

    pressedKeys = []
    now = time.time()
    currentPressed = ScanMatrix()

    for r in range(4):
        for c in range(10):
            isPressed = (r, c) in currentPressed
            wasPressed = matrixState[r][c]

            if isPressed and not wasPressed:
                pressTime[r][c] = now

            if not isPressed and wasPressed:
                print(f"[RELEASE] Layer {currentLayer} -> ({r},{c})")
                pressTime[r][c] = 0

            if isPressed:
                isLong = (now - pressTime[r][c]) > longPressTime
                keyName = GetActiveKey(r, c, isLong)

                if not wasPressed:
                    pressType = "LONG" if isLong else "SHORT"
                    print(f"[PRESS] Layer {currentLayer} | {pressType} | Key: {keyName}")

                if keyName == 'LAYER_UP':
                    currentLayer = min(2, currentLayer + 1)
                    print(f"[LAYER] Switched to Layer {currentLayer}")
                    continue

                if keyName == 'LAYER_DOWN':
                    currentLayer = max(1, currentLayer - 1)
                    print(f"[LAYER] Switched to Layer {currentLayer}")
                    continue

                keyCode = keyMap.get(keyName, 0)
                if keyCode:
                    pressedKeys.append(keyCode)

            matrixState[r][c] = isPressed

    if pressedKeys:
        Keyboard.hold_key(0, *pressedKeys[:maxHidKeys])
    else:
        Keyboard.release_keys()

# ---------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------

def MainLoop():
    """Main keyboard loop."""
    print("[INFO] Matrix keyboard started")
    try:
        while True:
            UpdateKeyboard()
            time.sleep(scanDelay)
    except KeyboardInterrupt:
        print("\n[INFO] Exiting...")
    finally:
        CleanupMatrixKeyboard()

def CleanupMatrixKeyboard():
    """Cleanup GPIO and HID."""
    try:
        Keyboard.release_keys()
        for gpio in rowGpios + colGpios:
            try:
                gpio.close()
            except Exception:
                pass
        print("[OK] GPIO cleaned up")
    except Exception:
        pass

# ---------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    try:
        TestHid()
        SetupMatrixKeyboard()
        MainLoop()
    except Exception as error:
        print(f"[FATAL] {error}")
        CleanupMatrixKeyboard()

