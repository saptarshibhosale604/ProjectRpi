from flask import Flask, render_template, send_from_directory, jsonify
import json
import os

app = Flask(__name__)

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
    app.run(host="0.0.0.0", port=5002, debug=True)
