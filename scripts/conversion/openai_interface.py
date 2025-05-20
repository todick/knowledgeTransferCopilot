import click
import openai

def get_json_name_from_transcript(transcript_path):
    return transcript_path.replace(".mp3", "_transcript.txt")

def action(path):
    audio_path = path
   
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file, "your api-key here", )

    transcript_file_path = get_json_name_from_transcript(path)

    with open(transcript_file_path, "w") as f:
        f.write(str(transcript["text"]))


@click.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def main(path):   
    action(path)


if __name__ == '__main__':   
    main()

   