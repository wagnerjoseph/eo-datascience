from pathlib import Path
import yaml

def render_toc():
    p = Path("notebooks").glob('*.ipynb')
    files = [x.with_suffix('') for x in p if x.is_file()]
    files.sort()
    titles = [x.stem.split("_")[-1].title() for x in files]
    ls = [dict(caption="Preamble", chapters=[dict(file="notebooks/how-to-cite")])]
    for i in range(len(titles)):
        ls.append(dict(caption=titles[i], chapters=[dict(file=str(files[i]))]))

    toc = dict(
        format="jb-book",
        root="README",
        parts=ls
    )

    with open('_toc.yml', 'w+') as ff:
        yaml.dump(toc, ff)

def main():
    render_toc()

if __name__ == '__main__':
    main()