# README.md 
# code and circuit working 
# ms1,ms2,ms3 is not connected

import lgpio
import time

# GPIO pins (BCM numbering)
DIR = 14
STEP = 15
ENABLE = 18

# Open GPIO chip
h = lgpio.gpiochip_open(0)

lgpio.gpio_claim_output(h, STEP)
lgpio.gpio_claim_output(h, DIR)
lgpio.gpio_claim_output(h, ENABLE)

# Enable driver (LOW = enabled)
lgpio.gpio_write(h, ENABLE, 0)

def move(steps, direction, delay=0.001):
    lgpio.gpio_write(h, DIR, direction)
    for i in range(steps):
        lgpio.gpio_write(h, STEP, 1)
        time.sleep(delay)
        lgpio.gpio_write(h, STEP, 0)
        time.sleep(delay)

try:
    while True:
        print("Clockwise")
        move(200, 1)
        time.sleep(1)

        print("Anti-clockwise")
        move(200, 0)
        time.sleep(1)

except KeyboardInterrupt:
    pass

lgpio.gpio_write(h, ENABLE, 1)
lgpio.gpiochip_close(h)