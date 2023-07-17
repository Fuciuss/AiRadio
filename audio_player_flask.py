from flask import Flask, request
from queue import Queue
from pydub import AudioSegment
from pydub.playback import play
import threading
import os
import pickle
import time

app = Flask(__name__)

class QueueItem:
    def __init__(self, track_name, track_location):
        self.track_name = track_name
        self.track_location = track_location

song_queue = Queue()

CURRENT_TRACK = "smooth jazz"

def save_queue():
    with open('song_queue.pkl', 'wb') as f:
        pickle.dump(list(song_queue.queue), f)

def load_queue():
    try:
        with open('song_queue.pkl', 'rb') as f:
            items = pickle.load(f)
            switch = False
            for item in items:
                song_queue.put(item)
    except FileNotFoundError:
        pass  # If the file doesn't exist, that's fine; we'll just start with an empty queue.

load_queue()


@app.route('/')
def hello_world():
    return f"""
    <html>
    <body style="color: white; background-color: black; text">
        <h1>Hello, World!</h1>
        <h2>Now playing: {CURRENT_TRACK}</h2>
        <h2 id="time"></h2>""" + """
        <script>
            function displayTime() {
                var date = new Date();
                var h = date.getHours();
                var m = date.getMinutes();
                var s = date.getSeconds();

                // Update time every 1 second
                setTimeout(displayTime, 1000);

                h = h < 10 ? "0" + h : h;
                m = m < 10 ? "0" + m : m;
                s = s < 10 ? "0" + s : s;

                document.getElementById('time').innerHTML = h + ":" + m + ":" + s;
                    
    }


            displayTime();
        </script>
    </body>
    </html>
    """


from flask import jsonify

@app.route('/current_track')
def current_track():
    return jsonify(track=CURRENT_TRACK)


@app.route('/queuesongs', methods=['POST'])
def queue_songs():
    print(request.json)

    for track in request.json:
        print(track)
        song_queue.put(QueueItem(track['track_name'], track['track_location']))
        print(f"Queued song: {track['track_name']}")

    save_queue()
    play_songs()

    return request.json

def play_songs():
    global CURRENT_TRACK


    while True:
        if not song_queue.empty():
            audio_file_item = song_queue.get()  # Get an audio file item from the queue
            audio_file = audio_file_item.track_location

            audio_segment = AudioSegment.from_wav(audio_file)

            # Apply fade in and fade out
            audio_segment = audio_segment.fade_in(2000).fade_out(2000)
            global CURRENT_TRACK
            CURRENT_TRACK = audio_file_item.track_name

            # pydub.playback.play is used to play the audio_segment
            print(f'playing audio file: {audio_file_item.track_name}')
            play(audio_segment)

            save_queue()

        else:
            
            CURRENT_TRACK = ""

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':  # Check if this is the main process
        t = threading.Thread(target=play_songs)
        t.start()
    app.run(debug=True)
