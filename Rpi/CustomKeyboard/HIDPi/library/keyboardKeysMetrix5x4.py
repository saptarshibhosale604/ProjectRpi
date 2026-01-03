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
        ['1', '2', '3']]
        # ['Tab', 'L0', 'Shift', 'Del', 'Space']]

# Define GPIO pins for rows and columns
# COL_PINS = [26, 19, 13, 6, 5]   # Pin no: 37, 35, 33, 31, 29
# ROW_PINS = [21, 20, 16, 12]     # Pin no: 40, 38, 36, 32

ROW_PINS = [26, 19, 13, 6]     # Pin no: 37, 35, 33, 31
COL_PINS = [21, 20, 16, 12, 1]   # Pin no: 40, 38, 36, 32, 28
# COL_PINS = [21, 20, 16, 12, 7]   # Pin no: 40, 38, 36, 32, 26 

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


def scan_matrix():
    for r_idx, r_pin in enumerate(ROW_PINS):
        lgpio.gpio_write(h, r_pin, 1)
        for c_idx, c_pin in enumerate(COL_PINS):
            # print(f":: r_idx: {r_idx}, c_idx: {c_idx}, r_pin: {r_pin}, c_pin: {c_pin}")
            print(f":: r_idx: {r_idx}, c_idx: {c_idx}, r_pin: {r_pin}, c_pin: {c_pin}, lgpio.gpio_read(h, c_pin): {lgpio.gpio_read(h, c_pin)}")
            if lgpio.gpio_read(h, c_pin):
                key = keys[r_idx][c_idx]
                print(f"Pressed: {key}")
                # Send_key(0, f"KEY_{key.upper()}")
                Send_key(0, key)
                # time.sleep(0.01)  # debounce actual
                # time.sleep(0.5)  # debounce test
                time.sleep(0.05)  # debounce test
                # time.sleep(2)  # debounce test
        lgpio.gpio_write(h, r_pin, 0)

 
def Send_key(device_id, keyValue):
    print(f"Send_key({device_id}, {keyValue})")

    # Ignore bottom row keys
    if keyValue in ['Tab', 'L0', 'Shift', 'Del', 'Space']:
        print(f"Ignored special key: {keyValue}")
        return

    key = keyValue.upper()

    key_map = {
        'A': KEY_A,
        'B': KEY_B,
        'C': KEY_C,
        'D': KEY_D,
        'E': KEY_E,
        'F': KEY_F,
        'G': KEY_G,
        'H': KEY_H,
        'I': KEY_I,
        'J': KEY_J,
        'K': KEY_K,
        'L': KEY_L,
        'M': KEY_M,
        'N': KEY_N,
        'O': KEY_O,
        'P': KEY_P,
        'Q': KEY_Q,
        'R': KEY_R,
        'S': KEY_S,
        'T': KEY_T,
        'U': KEY_U,
        'V': KEY_V,
        'W': KEY_W,
        'X': KEY_X,
        'Y': KEY_Y,
        'Z': KEY_Z,
    }

    if key in key_map:
        Keyboard.send_key(0, key_map[key])
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

