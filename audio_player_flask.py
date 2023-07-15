from flask import Flask, request
from queue import Queue
from pydub import AudioSegment
from pydub.playback import play
import threading
import os

app = Flask(__name__)

class QueueItem:
    def __init__(self, track_name, track_location):
        self.track_name = track_name
        self.track_location = track_location

song_queue = Queue()

global CURRENT_TRACK
CURRENT_TRACK = "smooth jazz"


@app.route('/')
def hello_world():
    return f"""<div style="color: white; background-color: black; text">
    
    <h1>Hello, World!</h1>
    <h2>Now playing: {CURRENT_TRACK}</h2>
    
    
    </div>"""


@app.route('/queuesongs', methods=['POST'])
def queue_songs():
    print(request.json)

    for track in request.json:
        print(track)
        song_queue.put(QueueItem(track['track_name'], track['track_location']))
        print(f"Queued song: {track['track_name']}")

    return request.json

def play_songs():
    while True:
        if not song_queue.empty():
            audio_file_item = song_queue.get()  # Get an audio file item from the queue
            audio_file = audio_file_item.track_location

            audio_segment = AudioSegment.from_wav(audio_file)

            # Apply fade in and fade out
            audio_segment = audio_segment.fade_in(2000).fade_out(2000)

            # pydub.playback.play is used to play the audio_segment
            print(f'playing audio file: {audio_file_item.track_name}')
            play(audio_segment)
            CURRENT_TRACK = audio_file_item.track_name

        else:
            CURRENT_TRACK = ""

if __name__ == '__main__':
    t = threading.Thread(target=play_songs)
    t.start()
    app.run(debug=True)
