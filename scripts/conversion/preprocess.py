import click
import os


def merge_files(raw_folder, n, out_folder):
    raw_files = [f for f in os.listdir(raw_folder) if f.endswith(".txt") and f"Study-{n:02d}" in f]
    raw_files.sort()

    content = ""
    for raw_file in raw_files:
        print(f"  Found '{raw_file}'")

        with open(os.path.join(raw_folder, raw_file), "r") as f:
            content += f.read() + "\n"

    out_file = f"Study-{n:02d}.txt"
    print(f"  Merging into '{out_file}'")

    with open(os.path.join(out_folder, out_file), "w") as f:
        f.write(content)

    return os.path.join(out_folder, out_file)

def add_paragraphs(out_file):
    with open(out_file, "r") as f:
        content = f.read()

    content = content.replace("\r", "")
    content = content.replace(". ", ".\n")
    content = content.replace("? ", "?\n")
    content = content.replace("! ", "!\n")
    content = content.replace("...", "")

    content = "\n".join([s for s in content.split("\n") if s])

    with open(out_file, "w") as f:
        f.write(content)

def remove_filler_words(out_file):
    with open(out_file, "r") as f:
        content = f.read()

    content = content.replace("So.\n", "")
    content = content.replace("Ähm.\n", "")
    content = content.replace("Ähm\n", "")
    content = content.replace("Ähm...\n", "")
    content = content.replace("Äh...\n", "")
    content = content.replace("Äh\n", "")
    content = content.replace("Äh \n", "")
    content = content.replace("Ah.\n", "")
    content = content.replace("...ähm...\n", "")
    content = content.replace("...ah...\n", "")
    content = content.replace("Mh.\n", "")
    content = content.replace("Okay.\n", "")
    content = content.replace("Okay\n", "")
    content = content.replace("Ja.\n", "Ja. ")
    content = content.replace("ähm", "")
    content = content.replace("äh", "")

    with open(out_file, "w") as f:
        f.write(content)


def action(raw_folder, n, out_folder):
    out_file = merge_files(raw_folder, n, out_folder)
    remove_filler_words(out_file)
    add_paragraphs(out_file)
    remove_filler_words(out_file)

@click.command()
@click.argument('raw_folder', type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True))
@click.argument('n', type=int)
@click.argument('out_folder', type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True))
def main(raw_folder, n, out_folder):
    action(raw_folder, n, out_folder)
    
if __name__ == '__main__':
    main()

