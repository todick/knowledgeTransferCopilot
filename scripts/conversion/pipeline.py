import click
import split_audio
import openai_interface
import preprocess
import os

@click.command()
@click.option("-r", '--raw_folder', type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True),
                help="The folder where the raw data is stored", default="../audio")
@click.option("-o", '--out_folder', type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True),
                help="The folder where the output should be stored", default="transcripts/final")
@click.option('-n', type=int, help="The number of the study to process")
def main(raw_folder, n, out_folder):
    # do the conversion only if the audio file exists ass ogg, not as mp3
    audio_path_ogg = os.path.join(raw_folder, f"Study-{n:02d}.ogg")
    audio_path = os.path.join(raw_folder, f"Study-{n:02d}.mp3")
    
    if os.path.exists(audio_path_ogg):
        # first, convert the audio to mp3 using the sh script
        print(f"1/4 Convert input to mp3 ({audio_path_ogg})")

        if not os.path.exists(audio_path):
            os.system(f"sh convert_to_audio.sh {audio_path_ogg} {audio_path}")
        else:
            print(f"  Audio file already exists. Skipping conversion.")
    else:
        print(f"1/4 Skipped, is already an mp3 file.")

    # then, split the audio
    print(f"2/4 Split audio ({audio_path})")
    split_audio.action(audio_path)

    # now there are three new audios that have to be sent to Whisper
    audio_parts = [f for f in os.listdir(raw_folder) if f.endswith(".mp3") and f"Study-{n:02d}_" in f]
    audio_parts.sort()

    if len(audio_parts) != 3:
        print("  There are not exactly 3 audio parts!")
        print(audio_parts)
        return

    print("3/4 Create transcripts")
    i = 1
    for audio_part in audio_parts:
        p = os.path.join(raw_folder, audio_part)
        print(f"  Processing file {i}/3 ({p})")
        openai_interface.action(p)
        i += 1

    # this gives us 3 txt files we want to preprocess
    print("4/4 Preprocess transcripts")
    preprocess.action(raw_folder, n, out_folder)

    print("Done")
    
if __name__ == '__main__':
    main()
