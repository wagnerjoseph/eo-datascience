import os
import nbformat
from pathlib import Path
from bs4 import BeautifulSoup


def clean_up_frontmatter():
    # Define the path to the notebooks
    root = Path('./notebooks').resolve()
    nb_paths = [root / file for file in os.listdir(root) if file.endswith('.ipynb')]

    # Iterate over the notebooks
    for nb_path in nb_paths:
        # Load the notebook
        nb = nbformat.read(nb_path, as_version=4)
        if nb.cells[0].source.startswith('---'):
            #Load frontmatter
            fm = nb.cells[0].source.split('\n')

            # Extract the title and the subtitle
            title, subtitle = '', ''
            for line in fm:
                if line.startswith('title'):
                    title = line.split(': ')[1]
                if line.startswith('subtitle'):
                    subtitle = line.split(': ')[1]
            
            # Update the cell
            nb.cells[0].source = f'# {title}\n{subtitle}\n'
            
            # Save the notebook
            nbformat.write(nb, nb_path)

def clean_up_references():
    # Load the references.html file
    html_file_path = Path('_book/chapters/references.html')
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content)
    references_div = soup.find('div', {'id': 'refs', 'class': 'references csl-bib-body hanging-indent'})

    # Format the references as string
    references_list = []
    for ref in references_div.get_text().split('\n\n\n'):
        ref = ref.replace('\n\n', '')
        ref = ref.replace('\n', ' ')
        references_list.append(ref)

    # Indent the references
    #ref_list = ['\t' + ref for ref in references_list]

    # Merge the references into a single string
    output_str = '\n\n'.join(references_list)

    # Load the References notebook
    ref_nb_path = Path('./notebooks/references.ipynb').resolve()
    nb = nbformat.read(ref_nb_path, as_version=4)

    # Update the cell
    nb.cells[0].source = f'# References\n\n{output_str}'

    # Save the notebook
    nbformat.write(nb, ref_nb_path)

def main():
    clean_up_frontmatter()
    clean_up_references()


if __name__ == '__main__':
    main()