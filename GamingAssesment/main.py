#!/usr/bin/env python3
import csv
import os
from datetime import datetime

QUESTIONS = [
    "I often play longer than I planned (e.g., 'just one more game' turns into hours).",
    "I find it hard to stop playing even when I know I should (work, sleep, meals).",
    "Over the last 3 months, my average daily gaming time has increased.",
    "Gaming has caused me to start work late, miss deadlines, or lower my performance.",
    "I have skipped or shortened important tasks (emails, calls, errands, studying) because of gaming.",
    "I sometimes prioritize gaming over exercise, sleep, or basic chores.",
    "I stay up late to play and feel tired or sleepy the next day at work.",
    "I skip meals or eat poorly because I am focused on gaming.",
    "I notice more eye strain, headaches, or body pain related to long gaming sessions.",
    "I feel restless, irritable, or low when I cannot play or when I have to stop.",
    "I often think about games during work, meetings, or other activities.",
    "I mostly use gaming to escape stress, boredom, or negative emotions instead of mixing in other coping methods.",
    "I cancel or avoid social plans to stay home and play.",
    "People close to me (family, friends, partner) have complained about the amount of time I spend gaming.",
    "I prefer gaming to almost all offline activities most days.",
    "I hide or minimize my real gaming hours from others.",
    "I have tried to cut down on gaming but failed or slipped back to old patterns.",
    "I keep gaming even when I can clearly see negative consequences (health, work, relationships)."
]

CSV_FILE = "gaming_checklist_log.csv"


def ask_yes_no(prompt: str) -> int:
    """Ask a Yes/No question, return 1 for Yes, 0 for No."""
    while True:
        answer = input(f"{prompt} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return 1
        if answer in ("n", "no"):
            return 0
        print("Please answer with 'y' or 'n'.")


def main():
    print("Gaming Self-Assessment Checklist")
    print("Answer each question with 'y' (yes) or 'n' (no): ")

    timestamp = datetime.now().isoformat(timespec="seconds")

    responses = []
    for idx, q in enumerate(QUESTIONS, start=1):
        print(f" Question {idx}:")
        response = ask_yes_no(q)
        responses.append(response)

    total_yes = sum(responses)
    print(" --- Summary ---")
    print(f"Total 'Yes' answers: {total_yes} out of {len(QUESTIONS)}")

    header = ["timestamp"] + [f"q{i}" for i in range(1, len(QUESTIONS) + 1)] + ["total_yes"]
    row = [timestamp] + responses + [total_yes]

    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

    print(f" Responses saved to {CSV_FILE}")


if __name__ == "__main__":
    main()
