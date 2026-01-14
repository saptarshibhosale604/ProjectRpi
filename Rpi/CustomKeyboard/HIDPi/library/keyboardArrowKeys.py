import time
import math

from hidpi import Keyboard, Mouse
from hidpi.keyboard_keys import *
from hidpi.mouse_buttons import *

import glob
import os

# timeAfterKeyDetected = 0.1
timeAfterKeyDetected = 0.01

def test_hid():
    # Find the first available HID gadget device
    hid_devices = glob.glob('/dev/hidg*')
    if hid_devices:
        HID_DEVICE = hid_devices[0]  # Typically /dev/hidg0 for keyboard
        print(f"Using HID device: {HID_DEVICE}")
    else:
        raise RuntimeError("No HID gadget device found. Ensure USB gadget is configured.")


def test_keyboard():
    print("Testing keyboard...")
    time.sleep(1)
    #Keyboard.send_text("Hello, HIDPi!", delay=0.25)
    Keyboard.send_text("Hello AYUSH", delay=0.25)
    time.sleep(1)
    Keyboard.send_key(0, KEY_A, hold=1)
    time.sleep(1)
    Keyboard.hold_key(0, KEY_B)
    time.sleep(1)
    Keyboard.release_keys()
    time.sleep(1)

def test_mouse():
    print("Testing mouse...")
    time.sleep(1)
    
    radius = 5
    
    for angle in range(0, 360, 1):
        x = int(radius * math.cos(math.radians(angle)))
        y = int(radius * math.sin(math.radians(angle)))
        Mouse.move(x, y)
        time.sleep(0.01)


import RPi.GPIO as GPIO
import time

# Use BOARD numbering
GPIO.setmode(GPIO.BOARD)

# Define pin to key mapping
pin_key_map_02 = {
    31: 'y',  # GPIO6
    33: 'g',  # GPIO13
    35: 'h',  # GPIO19
    37: 'j'   # GPIO26
}
# pin_key_map = {
#     31: 'h',  # GPIO6
#     33: 'j',  # GPIO13
#     35: 'k',  # GPIO19
#     37: 'l'   # GPIO26
# }

# Setup pins as input
# for pin in pin_key_map:
for pin in pin_key_map_02:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("Monitoring pins. Press Ctrl+C to exit.")

def MapGPIOToKeyLoop():
    global timeAfterKeyDetected
    try:
        while True:
            # for pin, key in pin_key_map.items():
            for pin, key in pin_key_map_02.items():
                if GPIO.input(pin) == GPIO.HIGH:
                    print(key)
                    if(key == 'y'):
                        Keyboard.send_key(0, KEY_Y) # Forward
                        time.sleep(timeAfterKeyDetected)  # debounce
                    elif(key == 'h'):
                        Keyboard.send_key(0, KEY_H) # Backward
                        time.sleep(timeAfterKeyDetected)  # debounce
                    elif(key == 'g'):
                        Keyboard.send_key(0, KEY_G) # Left
                        time.sleep(timeAfterKeyDetected)  # debounce
                    elif(key == 'j'):
                        Keyboard.send_key(0, KEY_J) # Right
                        time.sleep(timeAfterKeyDetected)  # debounce
                    # if(key == 'h'):
                    #     Keyboard.send_key(0, KEY_H)
                    #     time.sleep(0.5)  # debounce
                    # elif(key == 'j'):
                    #     Keyboard.send_key(0, KEY_J)
                    #     time.sleep(0.5)  # debounce
                    # elif(key == 'k'):
                    #     Keyboard.send_key(0, KEY_K)
                    #     time.sleep(0.5)  # debounce
                    # elif(key == 'l'):
                    #     Keyboard.send_key(0, KEY_L)
                    #     time.sleep(0.5)  # debounce
                    else:
                        print(f"Unknown key for pin {pin}: {key}")
                    
            # time.sleep(0.1)  # debounce / reduce CPU usage

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    test_hid()
    test_keyboard()
    test_mouse()
    # MapGPIOToKeyLoop()
    print("Tested")
