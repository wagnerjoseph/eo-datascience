from pathlib import Path
import yaml


def render_toc(p):
    with open(p, "r") as ff:
        quarto_toc = yaml.safe_load(ff)
    toc = render_toc_(quarto_toc)
    with open("_toc.yml", "w+") as ff:
        yaml.dump(toc, ff)


def render_toc_(toc):
    ls = [dict(caption="Preamble", chapters=[dict(file="notebooks/how-to-cite")])]
    ls += transform_quarto_toc(toc)
    ls += [dict(caption="References", chapters=[dict(file="notebooks/references")])]
    return dict(format="jb-book", root="README", parts=ls)


def transform_quarto_toc(toc):
    return [rename_keys_section(i) for i in extract_section(toc)]


def extract_section(toc):
    return toc["book"]["chapters"][1:-1]


def rename_keys_section(section):
    section = dict(zip(["caption", "chapters"], section.values()))
    try:
        section["chapters"] = [{"file": rename_file_path(i)} for i in section["chapters"]]
    except KeyError:
        pass
    return section


def rename_file_path(file_path):
    return str(Path("notebooks") / Path(file_path).stem)


def main():
    render_toc(p=Path("_quarto.yml").absolute().as_posix())


if __name__ == "__main__":
    main()
