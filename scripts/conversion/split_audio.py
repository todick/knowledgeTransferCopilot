import click
import math
import os
from pydub import AudioSegment

def get_new_filename(transcript_path, part):
    return transcript_path.replace(".mp3", f"_{part}.mp3")

def single_split(from_min, to_min, split_filename, audio):
    if os.path.exists(split_filename):
        print(f"  {split_filename} already exists. Skipping.")
        return

    t1 = from_min * 60 * 1000
    t2 = to_min * 60 * 1000
    split_audio = audio[t1:t2]
    split_audio.export(split_filename, format="mp3")
    

def multiple_split(audio_file, audio, min_per_split):
    total_mins = math.ceil(audio.duration_seconds / 60)
    for i in range(0, total_mins, min_per_split):
        single_split(i, i + min_per_split, get_new_filename(audio_file, f"{i}-{min(i + min_per_split, total_mins)}"), audio)
        print(f"  {i}-{min(i + min_per_split, total_mins)}: Done")
        if i == total_mins - min_per_split:
            print('  All splitted successfully')

def action(path):
    audio_path = path
    audio = AudioSegment.from_mp3(audio_path)
    multiple_split(audio_path, audio, 20)

@click.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def main(path):   
    action(path)

if __name__ == '__main__':   
    main()

   