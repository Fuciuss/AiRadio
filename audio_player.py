import threading
from queue import Queue
from pydub import AudioSegment
from pydub.playback import play
import os
import time


audio_queue = Queue()

def audio_player():
    while True:
        audio_file = audio_queue.get()  # Get an audio file from the queue
        if audio_file is None:  # If the file is None, break the loop
            break

        audio_segment = AudioSegment.from_wav(audio_file)

        # Apply fade in and fade out
        audio_segment = audio_segment.fade_in(2000).fade_out(2000)

        # pydub.playback.play is used to play the audio_segment
        print(f'playing audio file: {audio_file}')
        play(audio_segment)
