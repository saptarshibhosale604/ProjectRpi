import time
import math
import lgpio

from hidpi import Keyboard, Mouse
from hidpi.keyboard_keys import *
from hidpi.mouse_buttons import *

# Define the keys in a 5x4 matrix layout
keys = [['Q', 'W', 'E', 'R', 'T'],
        ['A', 'S', 'D', 'F', 'G'],
        ['Z', 'X', 'C', 'V', 'B'],        
        ['Tab', 'L0', 'Shift', 'Del', 'Space']]

ROW_PINS = [26, 19, 13, 6]     # Rows as outputs
COL_PINS = [21, 20, 16, 12, 1] # Columns as inputs

# Open GPIO chip
h = lgpio.gpiochip_open(0)

# Setup rows as output low
for row in ROW_PINS:
    lgpio.gpio_claim_output(h, row, 0)

# Setup columns as input (add pull-down if noisy: lgpio.gpio_set_pull_up_down(h, col, lgpio.LGPIO_PULL_DOWN))
for col in COL_PINS:
    lgpio.gpio_claim_input(h, col)

# Track state: set of (row_idx, col_idx) tuples for pressed keys
pressed_keys = set()

# Debounce: dict of (r,c): first_detected_time
key_debounce = {}

DEBOUNCE_MS = 50
SCAN_INTERVAL = 0.01  # Fast scan for responsiveness [web:16]

def get_keycode(key_label):
    """Map label to KEY_ constant."""
    if key_label in ['Tab', 'L0', 'Shift', 'Del', 'Space']:
        print(f"Ignored special key: {key_label}")
        return None
    
    key_map = {
        'A': KEY_A, 'B': KEY_B, 'C': KEY_C, 'D': KEY_D, 'E': KEY_E,
        'F': KEY_F, 'G': KEY_G, 'Q': KEY_Q, 'W': KEY_W, 'R': KEY_R,
        'T': KEY_T, 'Z': KEY_Z, 'X': KEY_X, 'S': KEY_S, 'V': KEY_V,
    }
    key = key_label.upper()
    return key_map.get(key)

def scan_matrix(kbd):
    global pressed_keys, key_debounce
    now = time.time() * 1000  # ms
    
    current_pressed = set()
    
    # Scan all rows
    for r_idx, r_pin in enumerate(ROW_PINS):
        lgpio.gpio_write(h, r_pin, 1)
        for c_idx, c_pin in enumerate(COL_PINS):
            if lgpio.gpio_read(h, c_pin):
                pos = (r_idx, c_idx)
                current_pressed.add(pos)
        lgpio.gpio_write(h, r_pin, 0)
    
    # Process transitions
    newly_pressed = current_pressed - pressed_keys
    released = pressed_keys - current_pressed
    
    # Handle releases first (cleanup)
    for pos in released:
        r_idx, c_idx = pos
        key_label = keys[r_idx][c_idx]
        keycode = get_keycode(key_label)
        if keycode:
            kbd.release(keycode)
            print(f"Released: {key_label}")
        key_debounce.pop(pos, None)  # Clear debounce
    
    # Handle new presses (debounce)
    for pos in newly_pressed:
        r_idx, c_idx = pos
        key_label = keys[r_idx][c_idx]
        keycode = get_keycode(key_label)
        if not keycode:
            continue
        if pos not in key_debounce:
            key_debounce[pos] = now
        if now - key_debounce[pos] >= DEBOUNCE_MS:
            # kbd.press(keycode)
            kbd.hold_key(keycode)
            print(f"Pressed (held): {key_label}")
            del key_debounce[pos]  # Debounced, track as pressed
    
    # Update state (only fully debounced presses)
    for pos in newly_pressed:
        if pos in key_debounce:  # Still debouncing
            pass
        else:
            pressed_keys.add(pos)
    pressed_keys -= released
    
    # Send the HID report with current state [web:10]
    # kbd.send_hid_report()  # Or Keyboard.send_report() if named differently; check hidpi source

# Init HID
kbd = Keyboard()

try:
    print("Scanning matrix for holds/multi-keys... Ctrl+C to stop.")
    while True:
        scan_matrix(kbd)
        time.sleep(SCAN_INTERVAL)
except KeyboardInterrupt:
    print("\nReleasing all keys and exiting...")
    # kbd.release_all()
    kbd.release_keys()
finally:
    lgpio.gpiochip_close(h)


