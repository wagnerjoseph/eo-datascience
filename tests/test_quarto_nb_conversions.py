from pathlib import Path

import nbformat  # noqa
import pytest  # noqa
import yaml
from eo_datascience.clean_nb import (
    clean_up_frontmatter,
    convert_callout_notes,
    convert_refs,
    find_ipynb,
    quarto_note_replace,
    quarto_ref_person_replace,
    quarto_ref_time_replace,
    set_kernel_all_notebooks,
    substitute_path,
)
from eo_datascience.render_sfinx_toc import (
    _render_toc,
    extract_appendix,
    extract_main,
    rename_file_path,
    rename_keys_section,
    transform_appendix,
    transform_main,
)


def test_toc_conversion():
    mock_quarto_toc = """
    project:
      type: book
      pre-render:
        - make kernel
      post-render:
        - quarto convert chapters/references.qmd
        - make post-render

    book:
      title: "Earth Observation Datascience"
      author: ""
      date: "10 January 2025"
      chapters:
        - index.qmd
        - part: chapters/courses/microwave-remote-sensing.qmd
          chapters:
            - chapters/courses/microwave-remote-sensing/01_in_class_exercise.qmd
            - chapters/courses/microwave-remote-sensing/02_in_class_exercise.qmd
      appendices:
        - part: chapters/templates/prereqs-templates.qmd
          chapters:
            - chapters/templates/classification.qmd
        - part: chapters/tutorials/prereqs-tutorials.qmd
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
      - file: notebooks/templates/prereqs-templates
        sections:
          - file: notebooks/templates/classification
    - caption: Tutorials
      chapters:
      - file: notebooks/tutorials/prereqs-tutorials
        sections:
          - file: notebooks/tutorials/floodmapping
    - caption: References
      chapters:
        - file: notebooks/references
    """

    quarto_toc = yaml.safe_load(mock_quarto_toc)

    main = extract_main(quarto_toc)
    assert len(main) == 1
    assert rename_file_path("tests/mock.qmd") == "tests/mock"
    assert rename_keys_section(main, "main") == [
        {
            "caption": "Courses",
            "chapters": [
                {
                    "file": "notebooks/courses/microwave-remote-sensing",
                    "sections": [
                        {
                            "file": "notebooks/courses/microwave-remote-"
                            + "sensing/01_in_class_exercise"
                        },
                        {
                            "file": "notebooks/courses/microwave-remote-"
                            + "sensing/02_in_class_exercise"
                        },
                    ],
                },
            ],
        }
    ]

    append = extract_appendix(quarto_toc)
    assert len(append) == 2
    assert rename_keys_section(append, "appendix") == [
        {
            "caption": "Templates",
            "chapters": [
                {
                    "file": "notebooks/templates/prereqs-templates",
                    "sections": [{"file": "notebooks/templates/classification"}],
                }
            ],
        },
        {
            "caption": "Tutorials",
            "chapters": [
                {
                    "file": "notebooks/tutorials/prereqs-tutorials",
                    "sections": [{"file": "notebooks/tutorials/floodmapping"}],
                }
            ],
        },
    ]

    quarto_toc_transform = transform_main(quarto_toc)
    assert len(main) == len(quarto_toc_transform)

    quarto_toc_transform = transform_appendix(quarto_toc)
    assert len(append) == len(quarto_toc_transform)

    assert _render_toc(quarto_toc) == yaml.safe_load(mock_jb_toc)


def test_remove_front_matter():
    assert (
        clean_up_frontmatter("./tests", None, False)["cells"][0]["cell_type"]
        == "markdown"
    )
    assert (
        clean_up_frontmatter("./tests", None, False)["cells"][0]["source"]
        == "# This a mock Jupyter file\n**We use it for testing**\n\nSome"
        + " other text, which should not be deleted!\n"
    )


def test_find_ipynb():
    assert find_ipynb("tests")[0].stem == "mock"


def test_substitute_path():
    nb_path = find_ipynb("tests")[0]
    assert substitute_path(nb_path, "./tests", "./tests/tests") == Path(
        "./tests/tests/mock.ipynb"
    )
    assert substitute_path(nb_path, "./tests", None) == Path("./tests/mock.ipynb")


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
        == r"lorem ipsum {cite:p}`anon2024` and {cite:p}`anon2025` and lorem"
        + " ipsum {cite:t}`anon2024` and {cite:t}`anon2025`"
    )


def test_conversion_of_callout_notes():
    rst = ":::{note}\nThis a callout note.\n:::"
    assert quarto_note_replace(r"::: {.callout-note}\nThis a callout note.\n:::") == rst
    assert convert_callout_notes("./tests", None, False)["cells"][1]["source"] == rst


def test_setting_kernelspec():
    meta_mock_nb = nbformat.read("tests/mock.ipynb", as_version=4).metadata
    kernel_display_name_mock_nb = meta_mock_nb.kernelspec.display_name
    kernel_name_mock_nb = meta_mock_nb.kernelspec.name
    new_meta_mock_nb = set_kernel_all_notebooks(dir="tests", save=False).metadata
    assert kernel_display_name_mock_nb != new_meta_mock_nb.kernelspec.display_name
    assert kernel_name_mock_nb != new_meta_mock_nb.kernelspec.name
