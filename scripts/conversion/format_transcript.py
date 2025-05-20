import click

def convert(out_file, in_files):
    result = []
    for file in in_files:
        with open(file, "r") as f:
            print(f"Reading {file}...")
            content = f.read().split(". ")
            content = filter(lambda l : len(l) > 0, content)
            content = list(map(lambda l : l + ("\n" if l[-1] == "." else ".\n"), content))
            content = list(map(lambda l : l[1:] if l[0] == " " else l, content))
            result.extend(content)
    
    print(f"Writing output to {out_file}")
    with open(out_file, "w") as f:
        f.writelines(result)

    print("Success")

@click.command()
@click.argument('out_file', type=click.Path(dir_okay=False, resolve_path=True), nargs = 1)
@click.argument('in_files', type=click.Path(exists=True, dir_okay=False, resolve_path=True), nargs = -1)
def main(out_file, in_files):   
    convert(out_file, in_files)    


if __name__ == '__main__':   
    main()

   