# Shift is getting printed when holding A,
# But not getting pressed

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

# Define GPIO pins for rows and columns
COL_PINS = [26, 19, 13, 6, 5]   # Pin no: 37, 35, 33, 31, 29
ROW_PINS = [21, 20, 16, 12]     # Pin no: 40, 38, 36, 32

# Open the default GPIO chip
h = lgpio.gpiochip_open(0)

# Claim row pins as output
for row in ROW_PINS:
    lgpio.gpio_claim_output(h, row, 0)

# Claim column pins as input (no pull specified)
for col in COL_PINS:
    lgpio.gpio_claim_input(h, col)

# Claim column pins as input with pull-down
# for col in COL_PINS:
#     lgpio.gpio_claim_input(h, col)
#     lgpio.gpio_set_pull_up_down(h, col, lgpio.LGPIO_PULL_DOWN)


# ----------- ONLY CHANGED / ADDED LINES BELOW ----------------
HOLD_THRESHOLD = 0.5  # 500ms

HOME_ROW_MODS = {
    'A': 'L_GUI',
    'S': 'L_ALT',
    'D': 'L_SHIFT',
    'F': 'L_CTRL',
    'G': 'TAB'
}

active_mod_mask = 0          # HID modifier bits   (Ctrl=0x01, Shift=0x02, …)
MOD_BITS = {
    'L_CTRL':  KEY_LEFT_CTRL,
    'L_SHIFT': KEY_LEFT_SHIFT,
    'L_ALT':   KEY_LEFT_ALT,
    'L_GUI':   KEY_LEFT_GUI,
}

key_map = {
    'A': KEY_A, 'B': KEY_B, 'C': KEY_C, 'D': KEY_D, 'E': KEY_E,
    'F': KEY_F, 'G': KEY_G, 'H': KEY_H, 'I': KEY_I, 'J': KEY_J,
    'K': KEY_K, 'L': KEY_L, 'M': KEY_M, 'N': KEY_N, 'O': KEY_O,
    'P': KEY_P, 'Q': KEY_Q, 'R': KEY_R, 'S': KEY_S, 'T': KEY_T,
    'U': KEY_U, 'V': KEY_V, 'W': KEY_W, 'X': KEY_X, 'Y': KEY_Y, 'Z': KEY_Z,
    'TAB': KEY_TAB,
    # 'L_SHIFT': KEY_LEFT_SHIFT,
    # 'L_CTRL': KEY_LEFT_CTRL,
    # 'L_ALT': KEY_LEFT_ALT,
    # 'L_GUI': KEY_LEFT_GUI,
    # # 'L_TAB': KEY_TAB
}

pressed    = {k: False for row in keys for k in row}
press_ts   = {}
mod_active = {k: False for k in HOME_ROW_MODS}
action = None

def scan_matrix():
    now = time.time()

    for r_idx, r_pin in enumerate(ROW_PINS):
        lgpio.gpio_write(h, r_pin, 1)

        for c_idx, c_pin in enumerate(COL_PINS):
            key = keys[r_idx][c_idx]
            is_down = bool(lgpio.gpio_read(h, c_pin))

            # Key down edge
            if is_down and not pressed[key]:
                pressed[key] = True
                press_ts[key] = now

            global active_mod_mask
            global action

            # Held: activate mod if long enough
            # Long‑hold detected → turn the modifier bit on
            if is_down and key in HOME_ROW_MODS and not mod_active[key]:
                if now - press_ts[key] >= HOLD_THRESHOLD:
                    if action in MOD_BITS:
                         active_mod_mask |= MOD_BITS[action]
                         print("KeyDown, Activated mod, Mod saved:", HOME_ROW_MODS[key])
                    # Tab is not a real modifier, just mark it active
                    mod_active[key] = True          # remember we turned it on

            # Key up edge
            if not is_down and pressed[key]:
                pressed[key] = False

                if key in HOME_ROW_MODS and mod_active[key]:
                     action = HOME_ROW_MODS[key]

                     if action in MOD_BITS:
                        active_mod_mask &= ~MOD_BITS[action]  # remove modifier
                        print("KeyUp, Deactivated mod, Mod cleared:", HOME_ROW_MODS[key])
                     elif action == 'TAB':
                        print("Psedo Mod Key")
                        #Keyboard.send_key(0, key_map['TAB'])  # modifier = 0
                        Send_key('TAB')

                     mod_active[key] = False

                else:
                    if key not in ['Tab', 'L0', 'Shift', 'Del', 'Space']:
                        # send_alpha(key)
                        # Send_key(0, key)
                        Send_key(key)

        lgpio.gpio_write(h, r_pin, 0)

 
def Send_key(keyValue):
    print(f"Send_key({keyValue})")
    # Ignore bottom row keys
    if keyValue in ['Tab', 'L0', 'Shift', 'Del', 'Space']:
        print(f"Ignored special key: {keyValue}")
        return

    # key = keyValue.upper()
    # key = keyValue

    global key_map
    global active_mod_mask

    if keyValue in key_map:
        # Keyboard.send_key(0, key_map[key])
        # Keyboard.send_key(key_map[key])
        Keyboard.send_key(active_mod_mask, key_map[keyValue])
        time.sleep(0.01)  # debounce actual
        # time.sleep(0.5)  # debounce test
        # time.sleep(2)  # debounce test
    else:
        print(f"Unknown or unsupported key: {keyValue}")
                    
try:
    print("Scanning keys... Press Ctrl+C to stop.")
    while True:
        scan_matrix()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    lgpio.gpiochip_close(h)


# ────  List of constants to test (symbolic names) ───────────────────────────────
import time

def test_all_keys():
    """
    Calls Keyboard.send_key(device_id, key) for every key value from 0x01 to 0xFF,
    with a 0.5‑second delay between each press.
    """
    time.sleep(2)  # Allow time for setup
    device_id = 0  # Assuming device_id is always 0 for this example
    # Keyboard.send_key(KEY_LEFT_SHIFT, 0)  # Press Ctrl to start
    #return  # Uncomment to skip sending all keys
    # return 0

    # for key in range(0x1, 0x100):  # 0x100 is 256, exclusive upper bound
    # for i in range(1, 256):  # from 1 to 255
    for i in range(8):
        value = 1 << i  # shift 1 left by i positions
        print(f"{value:08b}")  # print as 8-bit binary
        print(f"Sent key: 0x{value:02X}")
        Keyboard.send_key(value, device_id)
        try:
            # Keyboard.send_key(key, device_id)
            # print(f"{i:08b}")
            # print(f"Sent key: 0x{key:02X}")
            # time.sleep(0.5)
            #take user input to continue
            # input("Press Enter to continue to the next key...")
            # time.sleep(0.5)  # Delay between key presses
            # time.sleep(2)  # Delay between key presses
            time.sleep(5)  # Delay between key presses
        except Exception as e:
            print(f"Failed to send key 0x{key:02X}: {e}")

# test_all_keys()

