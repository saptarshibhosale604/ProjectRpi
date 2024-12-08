import gpiod
import time
LED_PIN = 17
chip = gpiod.Chip('gpiochip4')
led_line = chip.get_line(LED_PIN)
led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
try:
   while True:
       led_line.set_value(1)
       time.sleep(3)
       print("LED ON")
       led_line.set_value(0)
       time.sleep(3)
       print("LED OFF")
finally:
   led_line.release()
