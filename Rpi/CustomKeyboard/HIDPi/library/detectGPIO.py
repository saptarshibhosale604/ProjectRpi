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

try:
    while True:
        for pin, key in pin_key_map.items():
            if GPIO.input(pin) == GPIO.HIGH:
                print(key)
        time.sleep(0.1)  # debounce / reduce CPU usage

except KeyboardInterrupt:
    print("Exiting...")

finally:
    GPIO.cleanup()
