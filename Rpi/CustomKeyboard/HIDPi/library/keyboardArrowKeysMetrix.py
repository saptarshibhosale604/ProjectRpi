import time
import math

from hidpi import Keyboard, Mouse
from hidpi.keyboard_keys import *
from hidpi.mouse_buttons import *

# def test_keyboard():
#     print("Testing keyboard...")
#     time.sleep(1)
#     #Keyboard.send_text("Hello, HIDPi!", delay=0.25)
#     Keyboard.send_text("Hello AYUSH", delay=0.25)
#     time.sleep(1)
#     Keyboard.send_key(0, KEY_A, hold=1)
#     time.sleep(1)
#     Keyboard.hold_key(0, KEY_B)
#     time.sleep(1)
#     Keyboard.release_keys()
#     time.sleep(1)

# def test_mouse():
#     print("Testing mouse...")
#     time.sleep(1)
    
#     radius = 5
    
#     for angle in range(0, 360, 1):
#         x = int(radius * math.cos(math.radians(angle)))
#         y = int(radius * math.sin(math.radians(angle)))
#         Mouse.move(x, y)
#         time.sleep(0.01)


# import RPi.GPIO as GPIO
# import time

# # Use BOARD numbering
# GPIO.setmode(GPIO.BOARD)

# # Define pin to key mapping
# pin_key_map = {
#     31: 'h',  # GPIO6
#     33: 'j',  # GPIO13
#     35: 'k',  # GPIO19
#     37: 'l'   # GPIO26
# }

# # Setup pins as input
# for pin in pin_key_map:
#     GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# print("Monitoring pins. Press Ctrl+C to exit.")

# def MapGPIOToKeyLoop():
#     try:
#         while True:
#             for pin, key in pin_key_map.items():
#                 if GPIO.input(pin) == GPIO.HIGH:
#                     print(key)
#                     if(key == 'h'):
#                         Keyboard.send_key(0, KEY_H)
#                         time.sleep(0.5)  # debounce
#                     elif(key == 'j'):
#                         Keyboard.send_key(0, KEY_J)
#                         time.sleep(0.5)  # debounce
#                     elif(key == 'k'):
#                         Keyboard.send_key(0, KEY_K)
#                         time.sleep(0.5)  # debounce
#                     elif(key == 'l'):
#                         Keyboard.send_key(0, KEY_L)
#                         time.sleep(0.5)  # debounce
#                     else:
#                         print(f"Unknown key for pin {pin}: {key}")
                    
#             time.sleep(0.1)  # debounce / reduce CPU usage

#     except KeyboardInterrupt:
#         print("Exiting...")

#     finally:
#         GPIO.cleanup()

# if __name__ == "__main__":
#     # test_keyboard()
#     # test_mouse()
#     MapGPIOToKeyLoop()
#     print("Tested")

import lgpio
import time

keys = [['h', 'j'],
        ['k', 'l']]

ROW_PINS = [6, 13]
COL_PINS = [19, 26]

# Open the default GPIO chip
h = lgpio.gpiochip_open(0)

# Claim row pins as output
for row in ROW_PINS:
    lgpio.gpio_claim_output(h, row, 0)

# Claim column pins as input (no pull specified)
for col in COL_PINS:
    lgpio.gpio_claim_input(h, col)

def scan_matrix():
    for r_idx, r_pin in enumerate(ROW_PINS):
        lgpio.gpio_write(h, r_pin, 1)
        for c_idx, c_pin in enumerate(COL_PINS):
            if lgpio.gpio_read(h, c_pin):
                key = keys[r_idx][c_idx]
                print(f"Pressed: {key}")
                # Send_key(0, f"KEY_{key.upper()}")
                Send_key(0, key)
                time.sleep(0.01)  # debounce
        lgpio.gpio_write(h, r_pin, 0)

def Send_key(device_id, keyValue):
    print(f"Send_key({device_id}, {keyValue})")
    # Keyboard.send_key(0, KEY_H)
    key = keyValue.lower()
    if(key == 'h'):
        Keyboard.send_key(0, KEY_H)
        # time.sleep(0.5)  # debounce
    elif(key == 'j'):
        Keyboard.send_key(0, KEY_J)
        # time.sleep(0.5)  # debounce
    elif(key == 'k'):
        Keyboard.send_key(0, KEY_K)
        # time.sleep(0.5)  # debounce
    elif(key == 'l'):
        Keyboard.send_key(0, KEY_L)
        # time.sleep(0.5)  # debounce
    else:
        # print(f"Unknown key for pin {pin}: {key}")
        print(f"Unknown key ")
                    

try:
    print("Scanning keys... Press Ctrl+C to stop.")
    while True:
        scan_matrix()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    lgpio.gpiochip_close(h)

