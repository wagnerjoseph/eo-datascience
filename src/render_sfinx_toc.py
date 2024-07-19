from pathlib import Path
import yaml

p = Path("notebooks").glob('*.ipynb')
files = [x.with_suffix('') for x in p if x.is_file()]
titles = [x.stem.split("_")[-1].title() for x in files]
ls = []
for i in range(len(titles)):
    ls.append(dict(caption=titles[i], chapters=[dict(file=str(files[i]))]))
ls.append(dict(caption="Preamble", chapters=[dict(file="notebooks/how-to-cite")]))
ls.reverse()
toc = dict(
    format="jb-book",
    root="README",
    parts=ls
)

with open('_toc.yml', 'w+') as ff:
    yaml.dump(toc, ff)