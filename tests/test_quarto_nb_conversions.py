import nbformat
from pathlib import Path
import pytest
import yaml
from eo_datascience.render_sfinx_toc import (
    render_toc,
    render_toc_,
    transform_quarto_toc,
    extract_section,
    rename_keys_section,
    rename_file_path,
)
from eo_datascience.clean_nb import (
    clean_up_frontmatter,
    convert_refs,
    quarto_ref_person_replace,
    quarto_ref_time_replace,
    convert_callout_notes,
    quarto_note_replace,
    find_ipynb,
    substitute_path,
)


def test_toc_conversion():

    mock_quarto_toc = """
    project:
      type: book
      pre-render:
          - make kernel
      post-render: make post-render

    book:
      title: "Earth Observation Datascience"
      author: ""
      date: "7/10/2024"
      chapters:
          - index.qmd
          - part: chapters/courses/microwave-remote-sensing.qmd
          chapters:
              - chapters/courses/microwave-remote-sensing/01_in_class_exercise.qmd
              - chapters/courses/microwave-remote-sensing/02_in_class_exercise.qmd
      appendices:
          - part: "Templates"
          chapters:
              - chapters/templates/classification.qmd
          - part: "Tutorials"
          chapters:
              - chapters/tutorials/floodmapping.qmd
          - chapters/references.qmd
    """

    mock_jb_toc = """
    format: jb-book
    root: README
    parts:
    - caption: Preamble
      chapters:
        - file: notebooks/how-to-cite
    - caption: Courses
      chapters:
      - file: notebooks/courses/microwave-remote-sensing
      sections:
        - file: notebooks/courses/microwave-remote-sensing/01_in_class_exercise
        - file: notebooks/courses/microwave-remote-sensing/02_in_class_exercise
    - caption: Templates
      chapters:
        - file: notebooks/templates/classification
    - caption: Tutorials
        - file: notebooks/tutorials/floodmapping
    - caption: References
      chapters:
        - file: notebooks/references
    """

    ini = yaml.safe_load(mock_quarto_toc)
    sec = extract_section(ini)
    assert len(sec) == 3
    assert rename_file_path("chapters/01_notebook.qmd") == "notebooks/01_notebook"
    assert rename_keys_section(sec[0]) == {'caption': 'Name of Part 1', 'chapters': [{"file" : 'notebooks/01_notebook'}, {"file": 'notebooks/02_notebook'}]}

    quarto_toc_transform = transform_quarto_toc(ini)
    assert len(sec) == len(quarto_toc_transform)

    assert render_toc_(ini) == yaml.safe_load(mock_jb_toc)
    render_toc(Path("_quarto.yml").absolute().as_posix())


def test_remove_front_matter():
    assert clean_up_frontmatter("./tests", None, False)["cells"][0]["cell_type"] == "markdown"
    assert (
        clean_up_frontmatter("./tests", None, False)["cells"][0]["source"]
        == "# This a mock Jupyter file\n**We use it for testing**\n\nSome other text, which should not be deleted!\n"
    )


def test_find_ipynb():
    assert find_ipynb("tests")[0].stem == "mock"


def test_substitute_path():
    nb_path = find_ipynb("tests")[0]
    assert substitute_path(nb_path, "./tests", "./tests/tests") == Path('./tests/tests/mock.ipynb')
    assert substitute_path(nb_path, "./tests", None) == Path('./tests/mock.ipynb')


def test_conversion_of_refs():
    quarto = [
        r"lorem ipsum [@anon2024] and [@anon2025]",
        r"lorem ipsum @anon2024 and @anon2025",
    ]
    quarto[0] = quarto_ref_person_replace(quarto[0])
    quarto[1] = quarto_ref_time_replace(quarto[1])
    assert quarto == [
        r"lorem ipsum {cite:p}`anon2024` and {cite:p}`anon2025`",
        r"lorem ipsum {cite:t}`anon2024` and {cite:t}`anon2025`",
    ]
    assert (
        convert_refs("./tests", None, False)["cells"][2]["source"]
        == r"lorem ipsum {cite:p}`anon2024` and {cite:p}`anon2025` and lorem ipsum {cite:t}`anon2024` and {cite:t}`anon2025`"
    )


def test_conversion_of_callout_notes():
    rst = ":::{note}\nThis a callout note.\n:::"
    assert quarto_note_replace(r"::: {.callout-note}\nThis a callout note.\n:::") == rst
    assert convert_callout_notes("./tests", None, False)["cells"][1]["source"] == rst
