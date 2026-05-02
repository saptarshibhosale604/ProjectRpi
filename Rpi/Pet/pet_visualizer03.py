"""
README.md

# Pet Input Controller (pet_input.py)

## Overview
This script acts as a simple input controller for a digital/robotic pet system.
It allows a user to manually trigger events via keyboard input, which are then
written to a file (`event.txt`). Other systems (like a pet brain module) can read
this file and react accordingly.

## Features
- Simple CLI-based event input
- Clean mapping of user inputs to pet events
- File-based communication
- Graceful error handling
- Easy to extend

## Available Events
1 -> human_seen
2 -> touched
3 -> loud_noise
4 -> obstacle_near
5 -> low_battery
6 -> idle
q -> quit

## How It Works
- User enters a key
- Key is mapped to an event
- Event is written to `event.txt`
- External system reads and reacts

## Notes
- The script overwrites the event file on every input
- Designed for simplicity and reliability
"""

# =========================
# Project Info
# =========================
# Script Name: pet_input.py
# Purpose: CLI-based event generator for a pet system
# Author: Production-ready template
# =========================


# =========================
# Constants
# =========================
EVENT_FILE = "event.txt"


# =========================
# Functions
# =========================
def ShowMenu():
    """
    Display available input options to the user.
    """
    print("=== PET INPUT CONTROLLER ===")
    print("Type events and press enter:\n")

    print("Available events:")
    print("1 -> human_seen")
    print("2 -> touched")
    print("3 -> loud_noise")
    print("4 -> obstacle_near")
    print("5 -> low_battery")
    print("6 -> idle")
    print("q -> quit\n")


def GetEventMapping():
    """
    Return the mapping of user input to event names.

    Returns:
        dict: Mapping of keys to event strings
    """
    return {
        "1": "human_seen",
        "2": "touched",
        "3": "loud_noise",
        "4": "obstacle_near",
        "5": "low_battery",
        "6": "idle"
    }


def WriteEventToFile(eventName):
    """
    Write the given event to the event file.

    Args:
        eventName (str): Event to write
    """
    try:
        with open(EVENT_FILE, "w") as file:
            file.write(eventName)
        print(f"Sent: {eventName}")
    except Exception as error:
        print(f"[ERROR] Failed to write event: {error}")


def RunInputLoop():
    """
    Main loop to handle user input.
    """
    eventMapping = GetEventMapping()

    while True:
        try:
            userInput = input("Enter event: ").strip()

            if userInput.lower() == "q":
                print("Exiting...")
                break

            eventName = eventMapping.get(userInput)

            if eventName:
                WriteEventToFile(eventName)
            else:
                print("Invalid input")

        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user. Exiting...")
            break
        except Exception as error:
            print(f"[ERROR] Unexpected error: {error}")

"""
README.md

# Robot State Viewer

## Description
This script checks for the existence of a `Logs/states.json` file.
- If the file does not exist, it creates one using a predefined sample JSON structure.
- If the file exists, it prints selected values in a simple tabular format.

## Features
- Auto-creates missing JSON file
- Clean tabular console output
- Error handling with try-except
- Simple and easy-to-modify structure

## Usage
Run the script:
    python main.py

## Notes
- You can later extend this to update real sensor values.
"""

import os
import time
import json


def CreateSampleJson():
    """Returns a sample JSON structure."""
    samplestateJson = {
          "sensor_inputs": {
            "ultrasonic_sensor": "-",
            "touch_sensor": "-",
            "mic": "-",
            "battery_voltage_sensor": "-",
            "gyro": "-",
            "camera_module": "-"
          },
          "events": {
            "idle": "-",
            "touched": "-",
            "loud_noise": "-",
            "obstacle_near": "-",
            "low_battery": "-",
            "fall": "-",
            "new_object": "-",
            "known_object": "-",
            "human_seen": "-"
          },
          "emotions": {
            "attachment": "-",
            "energy": "-",
            "fear": "-",
            "curiosity": "-"
          },
          "actions": {
            "idle": "-",
            "sing": "-",
            "cry": "-",
            "dance": "-",
            "sleep": "-",
            "hide": "-",
            "charge": "-",
            "explore": "-",
            "follow_human": "-",
            "follow_object": "-"
          },
          "mechanical_output": {
            "speaker": "-",
            "display_eyes_expressions": "-",
            "leg_wheels_motors": "-"
          }
        }
    return samplestateJson


def EnsureFileExists(filePath):
    """Checks if file exists, if not creates it."""
    try:
        if not os.path.exists(filePath):
            os.makedirs(os.path.dirname(filePath), exist_ok=True)
            with open(filePath, "w") as file:
                json.dump(CreateSampleJson(), file, indent=4)
            print("File created at:", filePath)
            return False
        return True
    except Exception as e:
        print("Error while checking/creating file:", e)
        return False


def LoadJson(filePath):
    """Loads JSON data from file."""
    try:
        with open(filePath, "r") as file:
            return json.load(file)
    except Exception as e:
        print("Error loading JSON:", e)
        return None


def PrintTable(data):
    """Prints all top-level JSON blocks in a single aligned table."""
    try:
        if not isinstance(data, dict):
            print("Invalid data format")
            return

        mainBlocks = list(data.keys())

        blockKeys = {}
        blockValues = {}
        maxRows = 0

        for block in mainBlocks:
            items = data.get(block, {})
            keys = list(items.keys())
            values = list(items.values())

            blockKeys[block] = keys
            blockValues[block] = values

            maxRows = max(maxRows, len(keys))

        colWidth = 25

        # Header
        print("-" * (colWidth * len(mainBlocks)))
        header = ""
        for block in mainBlocks:
            header += f"{block:<{colWidth}}| "
        print(header)
        print("-" * (colWidth * len(mainBlocks)))

        # Rows
        for i in range(maxRows):

            # --- KEY ROW ---
            row = ""
            keyExists = []
            for block in mainBlocks:
                keys = blockKeys[block]
                if i < len(keys):
                    key = keys[i]
                    keyExists.append(True)
                else:
                    key = ""
                    keyExists.append(False)

                row += f"{key:<{colWidth}}| "
            print(row)

            # --- VALUE ROW ---
            row = ""
            for idx, block in enumerate(mainBlocks):
                values = blockValues[block]
                if keyExists[idx]:
                    val = values[i]
                else:
                    val = ""
                row += f"{str(val):<{colWidth}}| "
            print(row)

            # --- CURRENT ROW (only where key exists) ---
            row = ""
            for exists in keyExists:
                cell = "c" if exists else ""
                row += f"{cell:<{colWidth}}| "
            print(row)

            print()

    except Exception as e:
        print("Error printing table:", e)

def Main():
    """Main execution function."""
    filePath = os.path.join("Logs", "states.json")

    try:
        fileExists = EnsureFileExists(filePath)
        print(f"fileExists: {fileExists}")

        if fileExists:
            data = LoadJson(filePath)
            if data:
                PrintTable(data)

    except Exception as e:
        print("Unexpected error:", e)

counterLoop = 0

if __name__ == "__main__":
    while True:
        counterLoop+=1
        print(f"counterLoop: {counterLoop}")
        Main()
        time.sleep(4)

# =========================
# Entry Point
# =========================
# if __name__ == "__main__":
#     try:
#         ShowMenu()
#         RunInputLoop()
#     except Exception as error:
#         print(f"[FATAL] Application crashed: {error}")
