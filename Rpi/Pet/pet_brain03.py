"""
README.md
# Pet Brain (pet_brain.py)

## Description
A production-ready Python script that simulates a complete "pet brain" pipeline.
It reads sensor inputs, derives events, updates emotions, selects actions,
determines mechanical outputs, saves state to a JSON log, and prints a
visualizer-style table every loop cycle.

## Pipeline
    sensor_inputs → events → emotions → actions → mechanical_output

## Sensor Inputs (simulated randomly each cycle)
- ultrasonic_sensor   : distance in cm (float)
- touch_sensor        : True / False
- mic                 : True / False  (loud noise detected)
- battery_voltage_sensor : voltage (float)
- gyro                : True / False  (fall detected)
- camera_module       : "none" | "human" | "known_object" | "new_object"

## Events (derived from sensor inputs)
- idle, touched, loud_noise, obstacle_near, low_battery,
  fall, new_object, known_object, human_seen

## Emotions (float 0.0 – 1.0, decay each cycle)
- attachment, energy, fear, curiosity

## Actions (scored from emotions, best one selected)
- idle, sing, cry, dance, sleep, hide, charge,
  explore, follow_human, follow_object

## Mechanical Output (derived from selected action)
- speaker, display_eyes_expressions, leg_wheels_motors

## Log File
- Logs/state.json   (overwritten each cycle)

## Run
    python pet_brain.py

## Notes
- Sensor values are simulated; swap ReadSensorInputs() for real hardware reads.
- Loop delay is configurable via delayMainLoop (seconds).

## TODO
- all actions are not visible in print fucntion
"""

import os
import json
import time
import random

# -----------------------
# Config
# -----------------------
delayMainLoop = 1          # seconds between each brain cycle
logFilePath   = os.path.join("Logs", "state.json")
isTimeDecayEnable = False

# -----------------------
# Initial State
# -----------------------
def CreateInitialState():
    """Return a fresh state dictionary with default/placeholder values."""
    return {
        "sensor_inputs": {
            "ultrasonic_sensor":        "-",
            "touch_sensor":             "-",
            "mic":                      "-",
            "battery_voltage_sensor":   "-",
            "gyro":                     "-",
            "time_passed":              "-",
            "rtc":                      "-",
            "camera_module":            "-"
        },
        "events": {
            "idle":         False,
            "touched":      False,
            "loud_noise":   False,
            "obstacle_near":False,
            "low_battery":  False,
            "fall":         False,
            "time_of_day":  False,
            "charging":     False,
            "new_object":   False,
            "known_object": False,
            "human_seen":   False
        },
        "emotions": {
            "attachment":   0.0,
            "energy":       1.0,
            "fear":         0.0,
            "curiosity":    0.5,
            "boredom":      0.0,
            "happiness":    1.0,
            "loneliness":   0.0,
            "exitement":    0.0
        },
        "actions": {
            "idle":          0.0,
            "sing":          0.0,
            "cry":           0.0,
            "dance":         0.0,
            "sleep":         0.0,
            "action_randomizer":  0.0,
            "call_human":    0.0,
            "hide":          0.0,
            "charge":        0.0,
            "explore":       0.0,
            "follow_human":  0.0,
            "follow_object": 0.0
        },
        "mechanical_output": {
            "speaker":                  "-",
            "display_eyes_expressions": "-",
            "leg_wheels_motors":        "-",
            "speed_incrementer":        "-"
        }
    }

# Persistent state across cycles
state = CreateInitialState()

# Snapshot of state from the previous cycle — used to detect value changes in PrintTable
previousState = {}

# -----------------------
# Helpers
# -----------------------
def Clamp(value, lo=0.0, hi=1.0):
    """Clamp a float between lo and hi, rounded to 3 decimal places."""
    return round(max(lo, min(hi, value)), 3)

# -----------------------
# Step 1 – Read Sensor Inputs
# -----------------------

SENSOR_PROMPTS = {
    "ultrasonic_sensor":      "Ultrasonic distance (5.0–200.0 cm, e.g. 42.5): ",
    "touch_sensor":           "Touch sensor (True/False): ",
    "mic":                    "Mic triggered (True/False): ",
    "battery_voltage_sensor": "Battery voltage (3.2–4.2 V, e.g. 3.85): ",
    "gyro":                   "Gyro tilt detected (True/False): ",
    "camera_module":          "Camera result (none/human/known_object/new_object): ",
}

SENSOR_PARSERS = {
    "ultrasonic_sensor":      lambda v: round(float(v), 1),
    "touch_sensor":           lambda v: v.strip().lower() == "true",
    "mic":                    lambda v: v.strip().lower() == "true",
    "battery_voltage_sensor": lambda v: round(float(v), 2),
    "gyro":                   lambda v: v.strip().lower() == "true",
    "camera_module":          lambda v: v.strip().lower()
                                        if v.strip().lower() in {"none", "human", "known_object", "new_object"}
                                        else (_ for _ in ()).throw(ValueError(f"Invalid camera value: '{v}'")),
}

SENSOR_GENERATORS = {
    "ultrasonic_sensor":      lambda: round(random.uniform(5.0, 200.0), 1),
    "touch_sensor":           lambda: random.choice([True, False]),
    "mic":                    lambda: random.choice([True, False, False]),
    "battery_voltage_sensor": lambda: round(random.uniform(3.2, 4.2), 2),
    "gyro":                   lambda: random.choice([False, False, False, True]),
    "camera_module":          lambda: random.choice(["none", "none", "human",
                                                     "known_object", "new_object"]),
}
def ReadSensorInputs():
    """
    Asks the user to pick a sensor, then pick a value for it.
    If the user skips either prompt (Enter / 0), falls back to random.
    """
    try:
        sensorData = dict(state["sensor_inputs"])

        SENSOR_OPTIONS = {
            "ultrasonic_sensor":      [10.0, 25.0, 50.0, 100.0, 150.0, 200.0],
            "touch_sensor":           [True, False],
            "mic":                    [True, False],
            "battery_voltage_sensor": [3.2, 3.5, 3.7, 3.9, 4.0, 4.2],
            "gyro":                   [True, False],
            "camera_module":          ["none", "human", "known_object", "new_object"],
        }

        sensor_keys = list(SENSOR_OPTIONS.keys())

        # ── Step 1: Pick a sensor ─────────────────────────────────────────────
        input("\n[Sensor Override] Choose a sensor to set:")
        print(f"  0. random")
        print(f"  9. not any update at all")
        for i, key in enumerate(sensor_keys, start=1):
            print(f"  {i}. {key}")


        raw_sensor = input("Your choice: ").strip()
        sensor_choice = int(raw_sensor) if raw_sensor.isdigit() else 0

        if sensor_choice == 9:
            return sensorData

        if sensor_choice == 0 or sensor_choice > len(sensor_keys):
            # Random mode — update one random sensor
            key_to_update = random.choice(sensor_keys)
            sensorData[key_to_update] = SENSOR_GENERATORS[key_to_update]()
            print(f"  → (random) {key_to_update} = {sensorData[key_to_update]}")
            return sensorData

        chosen_sensor = sensor_keys[sensor_choice - 1]

        # ── Step 2: Pick a value for the chosen sensor ────────────────────────
        options = SENSOR_OPTIONS[chosen_sensor]
        print(f"\n[Value Override] Choose a value for '{chosen_sensor}' (0 = random):")
        for i, val in enumerate(options, start=1):
            print(f"  {i}. {val}")

        raw_value = input("Your choice: ").strip()
        value_choice = int(raw_value) if raw_value.isdigit() else 0

        if value_choice == 0 or value_choice > len(options):
            sensorData[chosen_sensor] = SENSOR_GENERATORS[chosen_sensor]()
            print(f"  → (random) {chosen_sensor} = {sensorData[chosen_sensor]}")
        else:
            sensorData[chosen_sensor] = options[value_choice - 1]
            print(f"  → {chosen_sensor} = {sensorData[chosen_sensor]}")

        return sensorData

    except Exception as error:
        print(f"[ERROR] ReadSensorInputs: {error}")
        return state["sensor_inputs"]

# -----------------------
# Step 2 – Update Events
# -----------------------
def UpdateEvents(sensorData):
    """
    Derive discrete events from raw sensor values.
    Returns an events dict with bool values.
    """
    try:
        events = {
            "idle":          False,
            "touched":       False,
            "loud_noise":    False,
            "obstacle_near": False,
            "low_battery":   False,
            "fall":          False,
            "new_object":    False,
            "known_object":  False,
            "human_seen":    False
        }

        # Obstacle: ultrasonic distance under 20 cm
        if isinstance(sensorData["ultrasonic_sensor"], (int, float)):
            if sensorData["ultrasonic_sensor"] < 20.0:
                events["obstacle_near"] = True

        # Touch
        if sensorData["touch_sensor"] is True:
            events["touched"] = True

        # Loud noise via mic
        if sensorData["mic"] is True:
            events["loud_noise"] = True

        # Low battery: below 3.5 V
        if isinstance(sensorData["battery_voltage_sensor"], (int, float)):
            if sensorData["battery_voltage_sensor"] < 3.5:
                events["low_battery"] = True

        # Fall via gyro
        if sensorData["gyro"] is True:
            events["fall"] = True

        # Camera events
        cam = sensorData["camera_module"]
        if cam == "human":
            events["human_seen"] = True
        elif cam == "known_object":
            events["known_object"] = True
        elif cam == "new_object":
            events["new_object"] = True

        # Idle: no significant event triggered
        anyActive = any([
            events["touched"], events["loud_noise"], events["obstacle_near"],
            events["low_battery"], events["fall"], events["new_object"],
            events["known_object"], events["human_seen"]
        ])
        if not anyActive:
            events["idle"] = True

        return events
    except Exception as error:
        print(f"[ERROR] UpdateEvents: {error}")
        return state["events"]

# -----------------------
# Step 3 – Update Emotions
# -----------------------
def UpdateEmotions(events, emotions):
    """
    Adjust emotion scores based on active events, then apply time decay.
    Modifies and returns the emotions dict.
    """
    try:
        e = dict(emotions)   # work on a copy

        # Event-driven adjustments
        if events.get("human_seen"):
            e["attachment"] += 0.2
            e["curiosity"]  += 0.1
        if events.get("touched"):
            e["attachment"] += 0.3
            e["fear"]       *= 0.5
        if events.get("loud_noise"):
            e["fear"]       += 0.4
        if events.get("obstacle_near"):
            e["fear"]       += 0.2
        if events.get("low_battery"):
            e["energy"]     -= 0.8
        if events.get("fall"):
            e["fear"]       += 0.3
            e["energy"]     -= 0.1
        if events.get("new_object"):
            e["curiosity"]  += 0.15
        if events.get("known_object"):
            e["curiosity"]  += 0.05
        if events.get("idle"):
            e["curiosity"]  += 0.02

        # Time decay
        if isTimeDecayEnable:
            e["fear"]       = e["fear"]       * 0.95
            e["attachment"] = e["attachment"] * 0.99
            e["curiosity"]  = e["curiosity"]  + 0.01
            e["energy"]     = e["energy"]     - 0.002

        # Clamp all
        for key in e:
            e[key] = Clamp(e[key])

        return e
    except Exception as error:
        print(f"[ERROR] UpdateEmotions: {error}")
        return emotions

# -----------------------
# Step 4 – Update Actions
# -----------------------
def UpdateActions(emotions):
    """
    Score every possible action based on current emotion values.
    Returns the actions dict (scores) and the name of the best action.
    """
    try:
        att = emotions["attachment"]
        eng = emotions["energy"]
        fea = emotions["fear"]
        cur = emotions["curiosity"]

        scores = {
            "explore":       Clamp(cur * eng),
            "follow_human":  Clamp(att * eng),
            "hide":          Clamp(fea * (1 - eng + 0.1)),
            "charge":        Clamp((1 - eng) * (1 - fea)),
            # "sleep":         Clamp((1 - eng) * (1 - fea)),
            "sleep":         Clamp(1 - eng),
            "dance":         Clamp(att * eng * (1 - fea)),
            "sing":          Clamp(cur * (1 - fea)),
            "cry":           Clamp(fea * att),
            "follow_object": Clamp(cur * eng * 0.8),
            "idle":          0.1
        }

        bestAction = max(scores, key=scores.get)
        return scores, bestAction
    except Exception as error:
        print(f"[ERROR] UpdateActions: {error}")
        return state["actions"], "idle"

# -----------------------
# Step 5 – Update Mechanical Output
# -----------------------
def UpdateMechanicalOutput(bestAction):
    """
    Map the selected action to physical/mechanical outputs.
    Returns a mechanical_output dict.
    """
    try:
        # Mapping table: action → (speaker, eyes_expression, leg_wheels)
        outputMap = {
            "explore":       ("ambient_hum",    "curious",   "forward_slow"),
            "follow_human":  ("happy_chirp",    "friendly",  "follow_target"),
            "hide":          ("silence",         "scared",    "reverse_fast"),
            "charge":        ("low_beep",        "sleepy",    "stop"),
            "sleep":         ("silence",         "closed",    "stop"),
            "dance":         ("music_beat",      "happy",     "spin_wiggle"),
            "sing":          ("melody",          "excited",   "sway"),
            "cry":           ("sad_tone",        "sad",       "stop"),
            "follow_object": ("curious_beep",   "focused",   "follow_target"),
            "idle":          ("silence",         "neutral",   "stop")
        }

        mapped = outputMap.get(bestAction, ("silence", "neutral", "stop"))
        mechanicalOutput = {
            "speaker":                  mapped[0],
            "display_eyes_expressions": mapped[1],
            "leg_wheels_motors":        mapped[2]
        }
        return mechanicalOutput
    except Exception as error:
        print(f"[ERROR] UpdateMechanicalOutput: {error}")
        return state["mechanical_output"]

# -----------------------
# Save State to JSON
# -----------------------
def SaveState(stateData):
    """
    Save the full state dictionary to Logs/state.json.
    Creates the Logs directory if it does not exist.
    """
    try:
        os.makedirs(os.path.dirname(logFilePath), exist_ok=True)
        with open(logFilePath, "w") as f:
            json.dump(stateData, f, indent=4)
    except Exception as error:
        print(f"[ERROR] SaveState: {error}")

# -----------------------
# Print Visualizer Table
# -----------------------
def PrintTable(data, prevData):
    """
    Print all top-level JSON blocks in a single aligned table,
    mirroring the format used in pet_visualizer.py.

    Marker row rules (per key):
      U  — value changed since the previous cycle  (Updated)
      c  — value is the same as the previous cycle (constant)
      '' — no key exists at this row index for this block
    """
    try:
        if not isinstance(data, dict):
            print("[WARN] PrintTable: data is not a dict")
            return

        mainBlocks = list(data.keys())
        blockKeys   = {}
        blockValues = {}
        maxRows = 0

        for block in mainBlocks:
            items  = data.get(block, {})
            keys   = list(items.keys())
            values = list(items.values())
            blockKeys[block]   = keys
            blockValues[block] = values
            maxRows = max(maxRows, len(keys))

        colWidth  = 25
        separator = "-" * (colWidth * len(mainBlocks))

        # Header row
        print(separator)
        header = ""
        for block in mainBlocks:
            header += f"{block:<{colWidth}}| "
        print(header)
        print(separator)

        # Data rows
        for i in range(maxRows):
            keyRow   = ""
            valueRow = ""
            markRow  = ""
            keyExists = []

            for block in mainBlocks:
                keys   = blockKeys[block]
                values = blockValues[block]

                if i < len(keys):
                    key = keys[i]
                    val = values[i]
                    keyExists.append(True)

                    # Compare current value to previous cycle's value
                    prevVal = prevData.get(block, {}).get(key)
                    if prevVal is None:
                        # First cycle — no previous value to compare against
                        # marker = "c"
                        marker = ""
                    elif str(val) != str(prevVal):
                        marker = "U"   # Updated: value changed
                    else:
                        # marker = "c"   # constant: value unchanged
                        marker = ""   # constant: value unchanged
                else:
                    key    = ""
                    val    = ""
                    marker = ""
                    keyExists.append(False)

                if marker:
                    keyRow += f"[U] {str(key):<{colWidth - 4}}| "
                else:
                    keyRow   += f"{str(key):<{colWidth}}| "
                valueRow += f"{str(val):<{colWidth}}| "
                # markRow  += f"{marker:<{colWidth}}| "

            print(keyRow)
            print(valueRow)
            # print(markRow)
            print()

    except Exception as error:
        print(f"[ERROR] PrintTable: {error}")

# -----------------------
# Main Loop
# -----------------------
def Main():
    """
    Main brain loop.
    Each cycle runs the full pipeline and updates the persistent state.
    """
    global state, previousState
    loopCounter = 0

    try:
        while True:
            loopCounter += 1
            print(f"\n{'='*60}")
            print(f"  Brain Cycle #{loopCounter}")
            print(f"{'='*60}")

            # --- Step 1: Read sensors ---
            sensorData = ReadSensorInputs()
            state["sensor_inputs"] = sensorData

            # --- Step 2: Derive events ---
            events = UpdateEvents(sensorData)
            state["events"] = events

            # --- Step 3: Update emotions ---
            emotions = UpdateEmotions(events, state["emotions"])
            state["emotions"] = emotions

            # --- Step 4: Score actions, pick best ---
            actionScores, bestAction = UpdateActions(emotions)
            state["actions"] = actionScores

            # --- Step 5: Mechanical output ---
            mechanicalOutput = UpdateMechanicalOutput(bestAction)
            state["mechanical_output"] = mechanicalOutput

            # --- Save state ---
            SaveState(state)

            # --- Print visualizer table (compare against previous cycle) ---
            PrintTable(state, previousState)

            # --- Snapshot current state for next cycle's change detection ---
            previousState = {
                block: dict(values)
                for block, values in state.items()
            }

            print(f"  ✅  Best Action → {bestAction}")
            # print(f"  💾  State saved to {logFilePath}")

            # input("Should I proceed: ")

            time.sleep(delayMainLoop)

    except KeyboardInterrupt:
        print("\n[INFO] Pet Brain stopped by user.")
    except Exception as error:
        print(f"[ERROR] Main: {error}")

# -----------------------
# Entry Point
# -----------------------
if __name__ == "__main__":
    Main()
