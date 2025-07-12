# Shift is getting printed when holding A,
# But not getting pressed

import time
import math
import lgpio

from hidpi import Keyboard, Mouse
from hidpi.keyboard_keys import *
from hidpi.mouse_buttons import *

# Define the keys in a 5x4 matrix layout
keys_layer01 = [['Q', 'W', 'E', 'R', 'T'],
        ['A', 'S', 'D', 'F', 'G'],
        ['Z', 'X', 'C', 'V', 'B'],        
        ['LAYERUP', 'LAYERDOWN', 'SPACE', 'ESC', 'CAPSLOCK']]

keys_layer02 = [['1', '2', '3', '4', '5'],
        ['!', '@', '#', '$', '%'],
        ['_', '-', '=', '+', '.'],        
        ['LAYERUP', 'LAYERDOWN', 'SPACE', 'ESC', 'CAPSLOCK']]

keys_layer03 = [['F1', 'F2', 'F3', 'F4', 'F5'],
        ['LEFT', 'DOWN', 'UP', 'RIGHT', '-'],
        ['-', '-', '-', '-', '-'],        
        ['LAYERUP', 'LAYERDOWN', 'SPACE', 'ESC', 'CAPSLOCK']]
key_layers = [keys_layer01, keys_layer02, keys_layer03]  # index == layer number

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

HOLD_THRESHOLD = 0.5  # 500ms

# Can work in all layers
SPECIAL_KEYS = {
    'LAYERUP', 
    'LAYERDOWN',
}
     
HOME_ROW_MODS = {
    # Original Key: Mod Key
    'A': 'L_GUI',
    'S': 'L_ALT',
    'D': 'L_SHIFT',
    'F': 'L_CTRL',
    'G': 'TAB'
}
LAYER02_SHIFT_MODS = {
    '!': '!',
    '@': '@',
    '#': '#',
    '$': '$',
    '%': '%',
    '_': '_',
    '+': '+' 
}

active_mod_mask = 0          # HID modifier bits   (Ctrl=0x01, Shift=0x02, …)
MOD_BITS = {
    'L_CTRL':  KEY_LEFT_CTRL,
    'L_SHIFT': KEY_LEFT_SHIFT,
    'L_ALT':   KEY_LEFT_ALT,
    'L_GUI':   KEY_LEFT_GUI,
}

key_map_layer01 = {
    'A': KEY_A, 'B': KEY_B, 'C': KEY_C, 'D': KEY_D, 'E': KEY_E,
    'F': KEY_F, 'G': KEY_G, 'H': KEY_H, 'I': KEY_I, 'J': KEY_J,
    'K': KEY_K, 'L': KEY_L, 'M': KEY_M, 'N': KEY_N, 'O': KEY_O,
    'P': KEY_P, 'Q': KEY_Q, 'R': KEY_R, 'S': KEY_S, 'T': KEY_T,
    'U': KEY_U, 'V': KEY_V, 'W': KEY_W, 'X': KEY_X, 'Y': KEY_Y, 'Z': KEY_Z,
    'TAB': KEY_TAB,
}
key_map_layer02 = {
    '1': KEY_1, '2': KEY_2, '3': KEY_3, '4': KEY_4, '5': KEY_5,
    '!': KEY_1, '@': KEY_2, '#': KEY_3, '$': KEY_4, '%': KEY_5,
    '_': KEY_MINUS, '-': KEY_MINUS, '=': KEY_EQUAL, '+': KEY_EQUAL, '.': KEY_PERIOD,
    'SPACE': KEY_SPACE, 'ESC': KEY_ESC,
    'TAB': KEY_TAB,
}
key_map_layer03 = {
    'F1': KEY_F1, 'F2': KEY_F2, 'F3': KEY_F3, 'F4': KEY_F4, 'F5': KEY_F5,
    'LEFT': KEY_LEFT, 'DOWN': KEY_DOWN, 'UP': KEY_UP, 'RIGHT': KEY_RIGHT,
    '-': KEY_MINUS,
}
key_map_layers   = [key_map_layer01, key_map_layer02, key_map_layer03]   # index == layer number

pressed_layer01    = {k: False for row in keys_layer01 for k in row}
pressed_layer02    = {k: False for row in keys_layer02 for k in row}
pressed_layer03    = {k: False for row in keys_layer03 for k in row}
pressed_layers   = [pressed_layer01, pressed_layer02, pressed_layer03]   # index == layer number

press_ts   = {}
mod_active = {k: False for k in HOME_ROW_MODS}
action = None

currentLayer = 1  # Current layer, Default: 1

def scan_matrix():
    global active_mod_mask
    global action
    global currentLayer

    now = time.time()

    for r_idx, r_pin in enumerate(ROW_PINS):
        lgpio.gpio_write(h, r_pin, 1)

        key = None
        for c_idx, c_pin in enumerate(COL_PINS):
            # if(currentLayer == 0):
            #     key = keys_layer01[r_idx][c_idx]
            # if(currentLayer == 1):
            #     key = keys_layer02[r_idx][c_idx]
            current_key_layer = key_layers[currentLayer-1]  # pick the right layer
            key = current_key_layer[r_idx][c_idx]

            is_down = bool(lgpio.gpio_read(h, c_pin))

            # Key down edge
            layer_pressed = pressed_layers[currentLayer-1]            # pick the right dict
            if is_down and not layer_pressed[key]: 
                layer_pressed[key] = True
                press_ts[key] = now

            # # Key down edge
            # if is_down and not pressed_layer01[key]:
            #     pressed_layer01[key] = True

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
            layer_pressed = pressed_layers[currentLayer-1]            # pick the right dict
            if not is_down and layer_pressed[key]:
            # if not is_down and pressed_layer01[key]:
                layer_pressed[key] = False
                # pressed_layer01[key] = False

                # print(f"key pressed_layer01: {key}")
                if key in SPECIAL_KEYS: # Special keys
                    print(f"Special key layer_pressed: {key} :: currentLayer: {currentLayer} ")
                    if key == 'LAYERUP':
                        print("Layer Up")
                        if currentLayer < 3:
                            currentLayer += 1
                    elif key == 'LAYERDOWN':
                        print("Layer Down")
                        if(currentLayer > 1):
                            currentLayer -= 1
                    print(f"changed currentLayer to {currentLayer}")

                
                elif currentLayer == 1:
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

                elif currentLayer == 2:
                    if key in LAYER02_SHIFT_MODS:
                        print(f"Layer02 Shift Mod Key: {key}")
                        active_mod_mask |= MOD_BITS['L_SHIFT']  # add modifier
                        Send_key(LAYER02_SHIFT_MODS[key])
                        active_mod_mask &= ~MOD_BITS['L_SHIFT']  # remove modifier
                    else:
                        print(f"Layer02 Key: {key}")
                        Send_key(key)

                elif currentLayer == 3:
                    print(f"Layer03 Key: {key}")
                    Send_key(key)

        lgpio.gpio_write(h, r_pin, 0)

 
def Send_key(keyValue):
    global key_map_layer01
    global key_map_layer02
    global active_mod_mask

    print(f"Send_key({keyValue}:: currentLayer:{currentLayer} :: active_mod_mask:{active_mod_mask})")

    # Ignore bottom row keys
    if keyValue in ['Tab', 'L0', 'Shift', 'Del', 'Space']:
        print(f"Ignored special key: {keyValue}")
        return

    # key = keyValue.upper()
    # key = keyValue

    current_key_map_layer = key_map_layers[currentLayer-1]            # pick the right dict

    # if(keyValue in key_map_layer01 or keyValue in key_map_layer02):
    if(keyValue in current_key_map_layer):
        # Keyboard.send_key(0, key_map[key])
        # Keyboard.send_key(key_map[key])
        # layer_pressed = pressed_layers[currentLayer-1]            # pick the right dict
        # current_key_map_layer = key_map_layers[currentLayer-1]            # pick the right dict
        # if (currentLayer == 0):
        #     Keyboard.send_key(active_mod_mask, key_map_layer01[keyValue])
        # elif (currentLayer == 1):
        #     Keyboard.send_key(active_mod_mask, key_map_layer02[keyValue])
        Keyboard.send_key(active_mod_mask, current_key_map_layer[keyValue])
        time.sleep(0.02)  # debounce actual

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

