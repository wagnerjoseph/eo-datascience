import argparse
from pathlib import Path
from typing import Literal

import yaml
from eo_datascience.clean_nb import substitute_path


def render_toc(p, out="."):
    with open(p, "r") as ff:
        quarto_toc = yaml.safe_load(ff)
    toc = _render_toc(quarto_toc)
    with open((Path(out) / "_toc.yml").resolve().as_posix(), "w+") as ff:
        yaml.dump(toc, ff)


def _render_toc(toc):
    ls = [dict(caption="Preamble", chapters=[dict(file="notebooks/how-to-cite")])]
    ls += transform_main(toc) + transform_appendix(toc)
    ls += [dict(caption="References", chapters=[dict(file="notebooks/references")])]
    return dict(format="jb-book", root="README", parts=ls)


def extract_main(toc):
    return toc["book"]["chapters"][1:]


def extract_appendix(toc):
    return toc["book"]["appendices"][:-1]


def transform_main(toc):
    return rename_keys_section(extract_main(toc), "main")


def transform_appendix(toc):
    return rename_keys_section(extract_appendix(toc), "appendix")


def rename_keys_section(
    sec,
    part: Literal["main", "appendix"],
):
    sections = sec.copy()
    for i, section in enumerate(sections):
        sections[i] = _rename_keys_section(section, ("part", "caption"))
        if part == "main":
            restructure_section_main(sections, i)
        elif part == "appendix":
            restructure_section_appendix(sections, i)
        else:
            sections[i]["caption"] = sections[i]["caption"][0]["file"]

    return sections


def restructure_section_main(sections, i):
    restruct = [
        {
            "file": sections[i]["caption"][i]["file"],
            "sections": sections[i]["chapters"],
        }
    ]
    sections[i]["chapters"] = restruct
    sections[i]["caption"] = "Courses"


def restructure_section_appendix(sections, i):
    restruct = [
        {
            "file": sections[i]["caption"][0]["file"],
            "sections": sections[i]["chapters"],
        }
    ]
    name = sections[i]["caption"][0]["file"].split("/")[1]
    sections[i]["chapters"] = restruct
    sections[i]["caption"] = name.capitalize()


def _rename_keys_section(section, key_rename):
    keys = [i.replace(*key_rename) for i in section.keys()]
    section = dict(zip(keys, section.values()))

    for key in section.keys():
        try:
            file_path = section[key]
            if not isinstance(file_path, list):
                file_path = [file_path]
            section[key] = [{"file": rename_file_path(i)} for i in file_path]
        except KeyError:
            pass
    return section


def rename_file_path(file_path):
    if Path(file_path).exists():
        file_path = str(
            substitute_path(file_path, "chapters", "notebooks").with_suffix("")
        )
    return file_path


def main():
    parser = argparse.ArgumentParser(description="Convert Quarto to Jupyter Book")
    parser.add_argument("out", type=str, help="Destination directory")
    args = parser.parse_args()
    render_toc(p=Path("_quarto.yml").absolute().as_posix(), out=args.out)


if __name__ == "__main__":
    main()
