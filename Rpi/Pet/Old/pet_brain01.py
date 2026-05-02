import random
import time

# -----------------------
# Emotion Engine
# -----------------------
emotion = {
    "energy": 1.0,
    "curiosity": 0.5,
    "fear": 0.0,
    "attachment": 0.0
}

# decay over time
def decay_emotions():
    emotion["fear"] *= 0.95
    emotion["attachment"] *= 0.99
    emotion["curiosity"] += 0.01
    emotion["energy"] -= 0.002

    # clamp values
    for k in emotion:
        emotion[k] = max(0.0, min(1.0, emotion[k]))

# -----------------------
# Event Handling
# -----------------------
def handle_event(event):
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

# -----------------------
# Behavior Selection
# -----------------------
def select_behavior():
    energy = emotion["energy"]
    curiosity = emotion["curiosity"]
    fear = emotion["fear"]
    attachment = emotion["attachment"]

    scores = {
        "explore": curiosity * energy,
        "follow_human": attachment * energy,
        "hide": fear * (1 - energy + 0.1),
        "charge": (1 - energy),
        "idle": 0.1
    }

    best = max(scores, key=scores.get)
    return best, scores

# -----------------------
# Actions (Mock)
# -----------------------
def act(behavior):
    if behavior == "explore":
        print("🐾 Exploring around...")
    elif behavior == "follow_human":
        print("👀 Following human!")
    elif behavior == "hide":
        print("😨 Hiding from danger!")
    elif behavior == "charge":
        print("🔋 Going to charge...")
    elif behavior == "idle":
        print("😴 Idling...")

# -----------------------
# Simulated Sensors
# -----------------------
def generate_random_event():
    events = [
        "human_seen",
        "touched",
        "loud_noise",
        "obstacle_near",
        "idle",
        None,
        None
    ]
    return random.choice(events)

# -----------------------
# Main Loop
# -----------------------
while True:
    event = generate_random_event()

    if event:
        print(f"\n⚡ Event: {event}")
        handle_event(event)

    decay_emotions()

    behavior, scores = select_behavior()

    print("Emotion:", emotion)
    print("Scores:", scores)
    print("Selected:", behavior)

    act(behavior)

    time.sleep(1)
