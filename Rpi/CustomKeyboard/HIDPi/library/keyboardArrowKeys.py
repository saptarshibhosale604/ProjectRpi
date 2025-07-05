import time
import math

from hidpi import Keyboard, Mouse
from hidpi.keyboard_keys import *
from hidpi.mouse_buttons import *

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
pin_key_map = {
    31: 'h',  # GPIO6
    33: 'j',  # GPIO13
    35: 'k',  # GPIO19
    37: 'l'   # GPIO26
}

# Setup pins as input
for pin in pin_key_map:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("Monitoring pins. Press Ctrl+C to exit.")

def MapGPIOToKeyLoop():
    try:
        while True:
            for pin, key in pin_key_map.items():
                if GPIO.input(pin) == GPIO.HIGH:
                    print(key)
                    if(key == 'h'):
                        Keyboard.send_key(0, KEY_H)
                        time.sleep(0.5)  # debounce
                    elif(key == 'j'):
                        Keyboard.send_key(0, KEY_J)
                        time.sleep(0.5)  # debounce
                    elif(key == 'k'):
                        Keyboard.send_key(0, KEY_K)
                        time.sleep(0.5)  # debounce
                    elif(key == 'l'):
                        Keyboard.send_key(0, KEY_L)
                        time.sleep(0.5)  # debounce
                    else:
                        print(f"Unknown key for pin {pin}: {key}")
                    
            time.sleep(0.1)  # debounce / reduce CPU usage

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    # test_keyboard()
    # test_mouse()
    MapGPIOToKeyLoop()
    print("Tested")
