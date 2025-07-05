import lgpio
import time

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, 19, 0)

for i in range(10):
    lgpio.gpio_write(h, 19, 1)
    time.sleep(0.5)
    lgpio.gpio_write(h, 19, 0)
    time.sleep(0.5)

lgpio.gpiochip_close(h)
