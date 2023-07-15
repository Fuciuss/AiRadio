from audiocraft.models import MusicGen

import time
import os
import random
from audiocraft.data.audio import audio_write
import torch
# import boto3
import requests

import time
from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"{func.__name__} took {elapsed_time} seconds")
        return result
    return wrapper

class MusicGenerator:


    def __init__(self, output_folder, model_size, track_count, duration, queue_url):
        self.output_folder = output_folder
        self.model = MusicGen.get_pretrained(model_size)
        self.set_generation_params(duration=duration)
        

        self.playlist = torch.Tensor([])
        self.track_count = track_count
        self.queue_url = queue_url


    
    def set_generation_params(self, top_k=250, duration=60, cfg_coef=8):
        self.model.set_generation_params(
            use_sampling=True,
            top_k=top_k,
            duration=duration,
            cfg_coef=cfg_coef
        )


    def select_random_prompts(self, count):
        prompts = [
            'Smooth jazz fusion, laidback saxophone, ambient, sultry piano, dynamic bassline',
            'Edgy punk, distorted guitar, high-energy, booming drums, raw vocals',
            'Funky afrobeat, vibrant brass, groovy, rhythmic percussion, upbeat bass',
            'Ethereal synthwave, dreamy synths, chill, soothing pads, hypnotic arpeggios',
            'Spicy salsa, vibrant horns, upbeat, pulsating rhythms, melodic bass',
            'Gritty blues, raw harmonica, mellow, haunting guitar, rhythmic drums',
            'Trippy dubstep, experimental synth, ambient, heavy-hitting bass, syncopated beats',
            'Mellow R&B, sultry vocals, chill, harmonic backing vocals, smooth bassline',
            'Upbeat pop, catchy hook, energetic, dynamic drums, melodic bass',
            'Groovy disco, funky guitar, upbeat, rhythmic bassline, harmonic strings',
            'Minimalistic techno, ambient pads, chill, pulsating kick drum, evolving synth melody',
            'Dreamy psychedelic rock, vintage guitar, laidback, hypnotic bass, rhythmic drums',
            'Experimental electronica, trippy synths, ambient, progressive structure, dynamic bassline',
            'Jazzy hip hop, smooth saxophone, mellow, chill beat, melodic bass',
            'Euphoric trance, pulsating synth, uplifting, energetic drums, harmonious pads',
            'Retro country, twangy guitar, laidback, soothing harmonica, rhythmic bass',
            'Vintage ska, upbeat horns, energetic, syncopated guitar, bouncing bass',
            'Sultry soul, emotive vocals, chill, rhythmic organ, mellow bassline',
            'Edgy punk, distorted guitar, high-energy, booming drums, raw vocals',
            'Classical piano piece, serene strings, ambient, melodic theme, dramatic orchestration',
            'Ambient classical, serene violin, chill, dreamy piano, ethereal orchestra',
            'Experimental grunge, distorted bass, gritty, raw vocals, booming drums',
            'Retro funk, groovy bassline, vibrant brass, rhythmic guitar, upbeat drums',
            'Mellow bossa nova, soothing guitar, laidback, smooth saxophone, rhythmic drums',
            'Dreamy shoegaze, ethereal guitars, chill, ambient synth, heavy-hitting drums',
            'Upbeat ska-punk, vibrant horns, energetic, distorted guitar, bouncing bass',
            'Vintage bluegrass, twangy banjo, laidback, rhythmic fiddle, dynamic bass',
            'Trippy ambient, experimental synth, chill, hypnotic pads, rhythmic drums',
            'Melodic metal, heavy guitar, energetic, haunting vocals, hard-hitting drums',
            'Sultry neo-soul, emotive vocals, mellow, harmonic keys, smooth bass',
            'Groovy nu-disco, funky bassline, upbeat, dynamic synth, rhythmic drums',
            'Euphoric hardstyle, pulsating synth, high-energy, heavy kick drum, rhythmic snares',
            'Laidback folk, acoustic guitar, soothing vocals, harmonic violin, mellow bass',
            'Experimental IDM, glitchy synths, ambient, progressive beats, dynamic bass',
            'Smooth reggae, chill guitar, laidback, rhythmic drums, melodic bass',
            'Gritty rock n roll, raw guitar, high-energy, booming drums, rhythmic bass',
            'Ethereal trip-hop, dreamy synth, chill, dynamic beat, smooth bass',
            'Funky swing, vibrant horns, upbeat, rhythmic double bass, energetic drums',
            'Ambient drone, ethereal synth, chill, evolving textures, hypnotic rhythm',
            'Energetic drum n bass, pulsating synth, high-energy, fast-paced drums, dynamic bassline'
        ]

        return random.sample(prompts, count)

    @timer
    def generate_first_section(self):

        # random_prompt = self.generate_random_prompt()
        # prompts = [self.generate_random_prompt() for i in range(self.track_count)]
        prompts = self.select_random_prompts()

        first_section = self.model.generate(prompts, progress=True)

        file_locations = self.write_multiple_clips(first_section, prompts, self.output_folder)

        self.upload_to_s3(files_to_upload=file_locations)

        return first_section

        
    def write_multiple_clips(self, clips, prompts, location):

        file_locations = []

        for i in range(clips.shape[0]):

            file_name = prompts[i].replace(" ", "_") + f"_{i}.wav"

            clip = clips.detach().cpu().float()[i]

            full_location = os.path.join(location, file_name)
            with open(full_location, 'wb') as file:
                # audio_write(
                #     file.name, clip, self.model.sample_rate, strategy="loudness",
                #     loudness_headroom_db=16, loudness_compressor=True, add_suffix=False)
                audio_write(
                    file.name, clip, self.model.sample_rate, strategy="loudness",
                    loudness_headroom_db=16, add_suffix=False)
                print(f'Saved to {file.name}')

            file_locations.append(full_location)
    
        return file_locations



    def generate_continuation(self, previous_section, continuation_prompts, overlap=5):

        last_moment = previous_section[:, :, -overlap*self.model.sample_rate:]

        continuation_section = self.model.generate_continuation(last_moment, self.model.sample_rate, descriptions=continuation_prompts, progress=True)

        full_continuation_tracks = torch.cat([previous_section[:, :, :-overlap*self.model.sample_rate], continuation_section], 2)

        # self.write_multiple_clips(full_continuation_tracks, continuation_prompts, self.output_folder)
        
        return full_continuation_tracks



    def generate_one_continuation(self):

        first = self.generate_first_section()

        continuation_prompts = [self.generate_random_prompt() for i in range(4)]

        cont = self.generate_continuation(first, continuation_prompts)

        self.write_multiple_clips(cont, continuation_prompts, self.output_folder)



    def generate_random_prompt(self):

        styles = ["funky", "groovy", "lofi", "chill", "ethereal",
        "smooth",
        "gritty",
        "edgy",
        "spicy",
        "dreamy",
        "retro",
        "vintage",
        "laidback",
        "experimental",
        "raw",
        "pulsating",
        "upbeat",
        "mellow",
        "euphoric",
        "sultry",
        "jazzy",
        "minimalistic",
        "ambient",
        "trippy"]

        genres = ["afrobeat", "reggae", "deep house", "hip hop", "trip hop",
        "synthwave",
        "techno",
        "bluegrass",
        "soul",
        "blues",
        "jazz fusion",
        "ambient",
        "disco",
        "dubstep",
        "trance",
        "psychedelic rock",
        "ska",
        "punk",
        "R&B",
        "funk",
        "electronica",
        "pop",
        "country",
        "classical"]

        styles_2 = ["vibey", "booming", "bouncy", "progressive", "melodic",
        "hard-hitting",
        "soothing",
        "hypnotic",
        "rhythmic",
        "haunting",
        "uplifting",
        "dynamic",
        "harmonic",
        "distorted",
        "percussive",
        "syncopated",
        "relaxing",
        "serene",
        "evocative",
        "eclectic",
        "staccato",
        "legato",
        "ornamental",
        "dramatic"]


        random_prompt = " ".join([random.choice(styles), random.choice(genres), random.choice(styles_2)])

        return random_prompt


    def upload_to_s3(self, files_to_upload):

        location = "s3://ai-radio/first-test/"
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('ai-radio')

        for file in files_to_upload:
            bucket.upload_file(file, f"first-test/{os.path.basename(file)}")

        


    def create_continuation_loop(self):
        pass



    def send_files_to_queue(self, files_to_upload):
            
            payload = [{"track_name": os.path.basename(file)[:10], "track_location": file} for file in files_to_upload]
            
            r = requests.post(self.queue_url, json=payload)
            print(f"Sent {len(files_to_upload)} files to queue at {self.queue_url} with status code: {r.status_code}")
            

    def one_continuation(self):


        self.model.set_generation_params(
            use_sampling=True,
            top_k=250,
            duration=30,
            cfg_coef=5
        )

        n_prompts = 9
        prompts = self.select_random_prompts(9)

        print(f"Generating {n_prompts} prompts of 30 seconds each")

        start_time = time.time()

        generated = self.model.generate(prompts, progress=True)

        overlap=5
        last_moment = generated[:, :, -overlap*self.model.sample_rate:]

        continuation_section = self.model.generate_continuation(last_moment, self.model.sample_rate, descriptions=prompts, progress=True)

        full_continuation_tracks = torch.cat([generated[:, :, :-overlap*self.model.sample_rate], continuation_section], 2)


        elapsed_time = time.time() - start_time


        print(f"took {elapsed_time} seconds to generate {n_prompts} prompts of {duration} seconds each")
        
        file_locations = self.write_multiple_clips(full_continuation_tracks, prompts, self.output_folder)







if __name__ == "__main__":

    model_size = "large"

    # Simple timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    # output_folder = f"/home/audiocraft/output_folder/{timestamp}"
    output_folder = f"/home/ubuntu/AiRadio/scratch_output/{timestamp}"
    track_count=5
    duration=30

    os.makedirs(output_folder)

    queue_url = 'http://127.0.0.1:5000/queuesongs'

    generator = MusicGenerator(output_folder, model_size, track_count, duration=duration, queue_url=queue_url)

    # generator.generate_one_continuation()

    # start_time = time.time()
    
    # first = generator.generate_first_section()
    generator.one_continuation()
    # elapsed_time = time.time() - start_time
    # print(f"First section took {elapsed_time} seconds")
