import lgpio
import time

DIR = 14
STEP = 15
ENABLE = 18

STEPS_PER_REV = 3200

h = lgpio.gpiochip_open(0)

lgpio.gpio_claim_output(h, DIR)
lgpio.gpio_claim_output(h, STEP)
lgpio.gpio_claim_output(h, ENABLE)

print("GPIO claimed")
print(f"DIR={DIR}, STEP={STEP}, ENABLE={ENABLE}")

lgpio.gpio_write(h, ENABLE, 0)
print("Driver ENABLED")

def rotate_revolutions(revs, direction, speed_rps=0.05):
    steps = int(revs * STEPS_PER_REV)
    delay = 1 / (STEPS_PER_REV * speed_rps)

    print(f"\nRotate: {revs} rev | Steps: {steps} | Dir: {direction}")
    print(f"Speed: {speed_rps} rps | Step delay: {delay:.6f}s")

    lgpio.gpio_write(h, DIR, direction)

    for i in range(steps):
        lgpio.gpio_write(h, STEP, 1)
        time.sleep(delay / 2)
        lgpio.gpio_write(h, STEP, 0)
        time.sleep(delay / 2)

        # Print every 500 steps so we don't spam
        if i % 500 == 0:
            print(f"Step {i}/{steps}")

    print("Rotation done")

print("Starting test...")

rotate_revolutions(1, 1)
time.sleep(2)
rotate_revolutions(1, 0)

print("Disabling driver")
lgpio.gpio_write(h, ENABLE, 1)
lgpio.gpiochip_close(h)
print("GPIO released")
