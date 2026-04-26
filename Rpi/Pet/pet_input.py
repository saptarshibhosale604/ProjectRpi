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


# =========================
# Entry Point
# =========================
if __name__ == "__main__":
    try:
        ShowMenu()
        RunInputLoop()
    except Exception as error:
        print(f"[FATAL] Application crashed: {error}")
