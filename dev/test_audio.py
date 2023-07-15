from pydub import AudioSegment
from pydub.playback import play

audio_file = './sample.wav'


audio_segment = AudioSegment.from_wav(audio_file)

# Apply fade in and fade out
audio_segment = audio_segment.fade_in(2000).fade_out(2000)

# pydub.playback.play is used to play the audio_segment
print(f'playing audio file: {audio_file}')
play(audio_segment)