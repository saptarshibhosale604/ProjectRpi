"""
README.md

# Pet Brain (pet_brain.py)

A simple, production-ready Python script that simulates a basic "pet brain" using an emotion engine.

## Features
- Emotion-based state system (energy, curiosity, fear, attachment)
- Event-driven updates via a file (`event.txt`)
- Behavior selection based on emotion scores
- Graceful error handling
- Simple and easy-to-understand logic

## How It Works
1. External systems write events into `event.txt`
2. Script reads and clears the file
3. Emotion state updates based on event
4. Behavior is selected based on current emotion
5. Loop runs continuously every second

## Example Events
- human_seen
- touched
- loud_noise
- obstacle_near
- low_battery
- idle

## Run
python pet_brain.py

## TODO
- add voice output
"""

import time
import os


# -----------------------
# Config
# -----------------------
eventFile = "event.txt"


# -----------------------
# Emotion Engine
# -----------------------
emotion = {
    "energy": 1.0,
    "curiosity": 0.5,
    "fear": 0.0,
    "attachment": 0.0
}


def ClampAndRound():
    """
    Clamp emotion values between 0 and 1 and round them.
    """
    try:
        for key in emotion:
            emotion[key] = round(max(0.0, min(1.0, emotion[key])), 3)
    except Exception as error:
        print(f"[ERROR] ClampAndRound: {error}")


# -----------------------
# Event Handling
# -----------------------
def HandleEvent(event):
    """
    Update emotion state based on incoming event.
    """
    try:
        if event == "human_seen":
            emotion["attachment"] += 0.2
            emotion["curiosity"] += 0.1

        elif event == "touched":
            emotion["attachment"] += 0.3
            emotion["fear"] *= 0.5

        elif event == "loud_noise":
            emotion["fear"] += 0.4

        elif event == "obstacle_near":
            emotion["fear"] += 0.2

        elif event == "low_battery":
            emotion["energy"] -= 0.3

        elif event == "idle":
            emotion["curiosity"] += 0.05

        ClampAndRound()

    except Exception as error:
        print(f"[ERROR] HandleEvent: {error}")


# -----------------------
# Decay
# -----------------------
def ApplyDecay():
    """
    Slowly decay or adjust emotions over time.
    """
    try:
        emotion["fear"] *= 0.95
        emotion["attachment"] *= 0.99
        emotion["curiosity"] += 0.01
        emotion["energy"] -= 0.002

        ClampAndRound()

    except Exception as error:
        print(f"[ERROR] ApplyDecay: {error}")


# -----------------------
# Behavior Selection
# -----------------------
def SelectBehavior():
    """
    Select behavior based on current emotion scores.
    """
    try:
        e = emotion

        scores = {
            "explore": round(e["curiosity"] * e["energy"], 3),
            "follow_human": round(e["attachment"] * e["energy"], 3),
            "hide": round(e["fear"] * (1 - e["energy"] + 0.1), 3),
            "charge": round((1 - e["energy"]), 3),
            "idle": 0.1
        }

        bestBehavior = max(scores, key=scores.get)
        return bestBehavior, scores

    except Exception as error:
        print(f"[ERROR] SelectBehavior: {error}")
        return "idle", {}


# -----------------------
# Read Event File
# -----------------------
def ReadEvent():
    """
    Read event from file and clear it.
    """
    try:
        if not os.path.exists(eventFile):
            return None

        with open(eventFile, "r") as file:
            data = file.read().strip()

        # Clear file
        open(eventFile, "w").close()

        return data if data else None

    except Exception as error:
        print(f"[ERROR] ReadEvent: {error}")
        return None


# -----------------------
# Main Loop
# -----------------------
def Main():
    """
    Main execution loop.
    """
    try:
        while True:
            event = ReadEvent()

            if event:
                print(f"\n⚡ Event: {event}")
                HandleEvent(event)

            # Optional decay (can enable if needed)
            # ApplyDecay()

            behavior, scores = SelectBehavior()

            print("\n==============================")
            print("Emotion:", emotion)
            print("Scores :", scores)
            print("Action :", behavior)
            print("==============================")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")
    except Exception as error:
        print(f"[ERROR] Main: {error}")


# -----------------------
# Entry Point
# -----------------------
if __name__ == "__main__":
    Main()
