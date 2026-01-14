# keyboard metrix 5x4x2
# key pressed, key released

import time
import math
from hidpi import Keyboard, Mouse
from hidpi.keyboard_keys import *
from hidpi.mouse_buttons import *
import glob
import os
from gpiozero import DigitalOutputDevice, Button

# Configuration
timeAfterKeyDetected = 0.01

def TestHid():
    """Find and validate HID gadget device."""
    try:
        hid_devices = glob.glob('/dev/hidg*')
        if hid_devices:
            print(f"Using HID device: {hid_devices[0]}")
            return hid_devices[0]
        else:
            raise RuntimeError("No HID gadget device found. Ensure USB gadget is configured.")
    except Exception as e:
        print(f"HID initialization error: {e}")
        raise

def TestKeyboard():
    """Test basic keyboard functionality."""
    print("Testing keyboard...")
    time.sleep(1)
    Keyboard.send_text("Hello Matrix Keyboard Pi5", delay=0.25)
    time.sleep(1)

def TestMouse():
    """Test basic mouse functionality."""
    print("Testing mouse...")
    time.sleep(1)
    radius = 5
    for angle in range(0, 360, 1):
        x = int(radius * math.cos(math.radians(angle)))
        y = int(radius * math.sin(math.radians(angle)))
        Mouse.move(x, y)
        time.sleep(0.01)

# 5x4 Matrix Keyboard Configuration (BCM GPIO numbers for Pi 5)
# KEYS_MATRIX = [
#     ['Q', 'W', 'E', 'R', 'T'],
#     ['A', 'S', 'D', 'F', 'G'],
#     ['Z', 'X', 'C', 'V', 'B'],
#     ['ESC', 'SPACE', 'TAB', '4', '5']
# ]
KEYS_MATRIX = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'SEMICOLON'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'COMMA', 'PERIOD', 'SLASH'],
    ['ESC', 'SPACE', 'TAB', '4', '5', '6', 'ENTER', 'BACKSPACE', '7', '8']
]

# BCM GPIO numbers for Raspberry Pi 5
ROW_PINS_BCM = [26, 19, 13, 6]      # GPIO26, GPIO19, GPIO13, GPIO6
COL_PINS_BCM = [21, 20, 16, 12, 1, 7, 8, 25, 24, 23]  # GPIO21, GPIO20, GPIO16, GPIO12, GPIO1 
#TODO write corrent pins

# Complete keycode mapping
KEY_MAP = {
    'Q': KEY_Q, 'W': KEY_W, 'E': KEY_E, 'R': KEY_R, 'T': KEY_T, 'Y': KEY_Y, 'U': KEY_U, 'I': KEY_I, 'O': KEY_O, 'P': KEY_P,
    'A': KEY_A, 'S': KEY_S, 'D': KEY_D, 'F': KEY_F, 'G': KEY_G, 'H': KEY_H, 'J': KEY_J, 'K': KEY_K, 'L': KEY_L, 'SEMICOLON': KEY_SEMICOLON,
    'Z': KEY_Z, 'X': KEY_X, 'C': KEY_C, 'V': KEY_V, 'B': KEY_B, 'N': KEY_N, 'M': KEY_M, 'COMMA': KEY_COMMA, 'PERIOD': KEY_PERIOD, 'SLASH': KEY_SLASH,
    '1': KEY_1, '2': KEY_2, '3': KEY_3, '4': KEY_4, '5': KEY_5, '6': KEY_6, '7': KEY_7, '8': KEY_8, '9': KEY_9, '0': KEY_0,
    'ESC': KEY_ESC, 'TAB': KEY_TAB, 'SPACE': KEY_SPACE, 'ENTER': KEY_ENTER, 'BACKSPACE': KEY_BACKSPACE
}

# GPIO objects
rowGpios = []
colGpios = []

# Track matrix state
# matrixStates = [[False for _ in range(5)] for _ in range(4)]
matrixStates = [[False for _ in range(10)] for _ in range(4)]

def SetupMatrixKeyboard():
    """Setup GPIO pins for matrix keyboard scanning using gpiozero."""
    global rowGpios, colGpios
    
    try:
        print("Setting up matrix keyboard for Raspberry Pi 5...")
        
        # Initialize row pins as DigitalOutputDevice (outputs)
        for rowPin in ROW_PINS_BCM:
            try:
                rowGpio = DigitalOutputDevice(rowPin, active_high=True, initial_value=False)
                rowGpios.append(rowGpio)
            except Exception as e:
                print(f"Error initializing row pin {rowPin}: {e}")
                raise
        
        # Initialize column pins as Button (inputs with pull_up=False)
        for colPin in COL_PINS_BCM:
            try:
                colGpio = Button(colPin, pull_up=False, bounce_time=0.01)
                colGpios.append(colGpio)
            except Exception as e:
                print(f"Error initializing column pin {colPin}: {e}")
                raise
        
        print("✓ Matrix keyboard initialized successfully")
        print(f"✓ Row pins (outputs): {ROW_PINS_BCM}")
        print(f"✓ Column pins (inputs): {COL_PINS_BCM}")
        
    except Exception as e:
        print(f"Critical error setting up matrix keyboard: {e}")
        CleanupMatrixKeyboard()
        raise

def ScanMatrixKeyboard():
    """Scan the 4x5 matrix and return pressed key positions."""
    pressedKeys = []
    
    try:
        for row in range(len(rowGpios)):
            rowGpios[row].on()
            time.sleep(0.001)
            
            for col in range(len(colGpios)):
                if colGpios[col].is_pressed:
                    pressedKeys.append((row, col))
            
            rowGpios[row].off()
    
    except Exception as e:
        print(f"Error scanning matrix: {e}")
    
    return pressedKeys

def UpdateHidKeysFromMatrix():
    """Update HID keyboard state based on matrix scan results."""
    try:
        pressedKeycodes = []
        releasedKeycodes = []
        
        currentPressed = ScanMatrixKeyboard()
        
        for row in range(4):
            # for col in range(5):
            for col in range(10):
                # input(f"row: {row}, col: {col}:: ")
                # print(f"row: {row}, col: {col}:: ")
                currentState = (row, col) in currentPressed
                # print(f"currentState: {currentState}")
                # if(currentState):
                #     print("true bruh")
                #     time.sleep(2)
                prevState = matrixStates[row][col]
                
                keyChar = KEYS_MATRIX[row][col]
                keycode = KEY_MAP.get(keyChar, 0)
                
                if currentState and not prevState:
                    print(f"{keyChar} pressed")
                elif not currentState and prevState:
                    print(f"{keyChar} released")
                    if keycode:
                        releasedKeycodes.append(keycode)
                
                if currentState and keycode:
                    pressedKeycodes.append(keycode)
                
                matrixStates[row][col] = currentState
        
        if pressedKeycodes:
            Keyboard.hold_key(0, *pressedKeycodes[:6])
        else:
            Keyboard.release_keys()
        
        if releasedKeycodes:
            Keyboard.release_keys()
            
    except Exception as e:
        print(f"Error updating HID keys: {e}")
        Keyboard.release_keys()

def MainMatrixKeyboardLoop():
    """Main loop for matrix keyboard scanning and HID reporting."""
    try:
        print("\n✓ Starting matrix keyboard monitoring for Raspberry Pi 5")
        print("✓ Press Ctrl+C to exit\n")
        
        while True:
            UpdateHidKeysFromMatrix()
            time.sleep(0.02)
            
    except KeyboardInterrupt:
        print("\n\nExiting matrix keyboard...")
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        CleanupMatrixKeyboard()

def CleanupMatrixKeyboard():
    """Cleanup GPIO resources and release keys."""
    try:
        Keyboard.release_keys()
        
        for rowGpio in rowGpios:
            try:
                rowGpio.close()
            except:
                pass
        
        for colGpio in colGpios:
            try:
                colGpio.close()
            except:
                pass
        
        print("GPIO cleaned up and keys released.")
        
    except Exception as e:
        print(f"Cleanup error: {e}")

if __name__ == "__main__":
    try:
        TestHid()
        SetupMatrixKeyboard()
        MainMatrixKeyboardLoop()
        
    # except KeyboardError as e:
    #     print(f"HID Error: {e}")
    except RuntimeError as e:
        print(f"Runtime Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        try:
            CleanupMatrixKeyboard()
        except:
            pass


