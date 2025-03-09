from flask import Flask, render_template, send_from_directory, jsonify
import json
import os
import threading
import time


app = Flask(__name__)
mode_file = "mode.txt"
last_mode = ""

# Function to watch for file changes
def watch_mode_file():
    global last_mode
    while True:
        try:
            with open(mode_file, "r") as file:
                mode = file.read().strip()
                if mode != last_mode:
                    last_mode = mode
                    print(f"Mode changed: {mode}")  # For debugging
        except FileNotFoundError:
            print("mode.txt not found, creating...")
            with open(mode_file, "w") as file:
                file.write("")
        time.sleep(2)  # Check every 2 seconds

def update_mode_file():
        with open(mode_file, "w") as file:
            file.write("normal")  # Update mode in file
        return jsonify({"message": "Mode updated", "mode": "normal"}), 200

# API route for frontend to fetch mode
@app.route("/get_mode", methods=["GET"])
def get_mode():
    try:
        with open(mode_file, "r") as file:
            mode = file.read().strip()
            #if(mode == "pause"):
            update_mode_file()
        return jsonify({"mode": mode})
    except FileNotFoundError:
        return jsonify({"mode": "unknown"})


# Load songs from JSON file
def load_songs():
    with open("/home/rpissb/Project/Python/MusicStreamingApp/songs.json", "r") as f:
        return json.load(f)

# Route to display songs
@app.route('/')
def index():
    songs = load_songs()
    return render_template('index.html', songs=songs)

# Route to stream music
@app.route('/play/<filename>')
def play_song(filename):
    return send_from_directory('static/music', filename)

# Route to get song metadata as JSON
@app.route('/songs')
def get_songs():
    return jsonify(load_songs())

if __name__ == '__main__':
    #app.run(debug=True)
    # Start the file watcher in a separate thread
    threading.Thread(target=watch_mode_file, daemon=True).start()
    app.run(host="0.0.0.0", port=5002, debug=True)
