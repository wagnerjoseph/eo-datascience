import os
import nbformat
from pathlib import Path
import re
import argparse


def clean_up_frontmatter(dir="./notebooks", out=None, save=True):
    # Define the path to the notebooks
    nb_paths = find_ipynb(dir)

    # Iterate over the notebooks
    for nb_path in nb_paths:
        # Load the notebook
        nb = nbformat.read(nb_path, as_version=4)
        if nb.cells[0].source.startswith("---"):
            # Load frontmatter
            fm = nb.cells[0].source.split("\n")

            # Extract the title and the subtitle and convert
            i = 1
            line = fm[i]
            new_text = []
            while not line.startswith("---"):
                if line.startswith("title"):
                    new_text.append(f"# {line.split(': ')[1]}")
                if line.startswith("subtitle"):
                    new_text.append(f"**{line.split(': ')[1]}**")

                i += 1
                line = fm[i]

            new_text += fm[i + 1 :]
            nb.cells[0].source = "\n".join(new_text) + "\n"
            nb.cells[0].cell_type = "markdown"
        # Save notebook
        nb_path = substitute_path(nb_path, dir, out)
        if save:
            nbformat.write(nb, nb_path)
        else:
            return nb


def convert_bibliography(nb_path="./notebooks/references.ipynb", out=None, save=True):
    nb_path = Path(nb_path)
    if nb_path.exists():
        nb = nbformat.read(nb_path, as_version=4)
        nb.cells[0].source = """# References

    ```{bibliography}
    ```
    """
        # Save the notebook
        nb_path = substitute_path(nb_path, nb_path.parent, out)
        if save:
            nbformat.write(nb, nb_path)
        else:
            return nb


def convert_callout_notes(dir="./notebooks", out=None, save=True):
    nb_paths = find_ipynb(dir)

    # Iterate over the notebooks
    for nb_path in nb_paths:
        # Load the notebook
        nb = nbformat.read(nb_path, as_version=4)
        for i in range(len(nb.cells)):
            if nb.cells[i]["cell_type"] == "markdown":
                nb.cells[i].source = quarto_note_replace(nb.cells[i].source)
        # Save the notebook
        nb_path = substitute_path(nb_path, dir, out)
        if save:
            nbformat.write(nb, nb_path)
        else:
            return nb


def quarto_note_replace(quarto):
    note_rst_start = r":::{note}"
    note_rst_end = r":::"
    nts = re.findall(r"(?<=:::\s\{\.callout\-note\})[^:::]+", quarto)
    for i in nts:
        quarto = re.sub(
            r":::\s\{\.callout\-note\}" + re.escape(i) + r":::",
            note_rst_start + i + note_rst_end,
            quarto,
        )
    return quarto


def convert_refs(dir="./notebooks", out=None, save=True):
    nb_paths = find_ipynb(dir)

    # Iterate over the notebooks
    for nb_path in nb_paths:
        # Load the notebook
        nb = nbformat.read(nb_path, as_version=4)
        for i in range(len(nb.cells)):
            if i != 0:
                if nb.cells[i]["cell_type"] == "markdown":
                    nb.cells[i].source = quarto_ref_figure_replace(nb.cells[i].source)
                    nb.cells[i].source = quarto_ref_person_replace(nb.cells[i].source)
                    nb.cells[i].source = quarto_ref_time_replace(nb.cells[i].source)
            nb

        # Save the notebook
        nb_path = substitute_path(nb_path, dir, out)
        if save:
            nbformat.write(nb, nb_path)
        else:
            return nb


def quarto_ref_figure_replace(quarto):
    bibs = re.findall(r"(?<=\(\@)[^\)]+", quarto)
    for i in bibs:
        quarto = re.sub(r"\(\@" + i + r"\)", "", quarto)
    return quarto


def quarto_ref_person_replace(quarto):
    bibs = re.findall(r"(?<=\[\@)[^\]]+", quarto)
    for i in bibs:
        quarto = re.sub(r"\[\@" + i + r"\]", r"{cite:p}`" + i + "`", quarto)
    return quarto


def quarto_ref_time_replace(quarto):
    bibs = re.findall(r"(?<=\@)[^\s]+", quarto)
    for i in bibs:
        quarto = re.sub(r"\@" + i, r"{cite:t}`" + i + "`", quarto)
    return quarto


def find_ipynb(dir):
    return list(Path(dir).rglob("*.ipynb"))


def substitute_path(nb_path, dir, out):
    if out is not None:
        nb_path = Path(str(nb_path).replace(str(Path(dir)), str(Path(out))))
        if not nb_path.exists():
            nb_path.parent.mkdir(parents=True, exist_ok=True)
    return nb_path


def main():
    parser = argparse.ArgumentParser(description="Convert Quarto to Jupyter Book")
    parser.add_argument("dir", type=str, help="Input Directory")
    parser.add_argument("out", type=str, help="Destination directory")
    args = parser.parse_args()

    clean_up_frontmatter(args.dir, args.out)
    convert_callout_notes(args.out)
    convert_refs(args.out)
    convert_bibliography(out=args.out)


if __name__ == "__main__":
    main()
