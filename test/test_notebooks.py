from pathlib import Path

import pytest
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
from nbconvert.preprocessors import TagRemovePreprocessor


RECIPE_DIRECTORIES = (
    "01-Cooking-Tutorials",
    "02-Easy-Recipes",
    "03-Advanced-Recipes",
    "04-Regional-Specialties",
)


def recipe_notebooks():
    notebooks = []
    for recipe_directory in RECIPE_DIRECTORIES:
        notebooks.extend(
            path
            for path in Path(recipe_directory).rglob("*.ipynb")
            if ".ipynb_checkpoints" not in path.parts
        )

    return sorted(notebooks)


def run_notebook(notebook_filename, tmp_path):
    '''
    Reads a notebook from a file, executes it, then writes the result back to a
    temporary file. If an error occurs while executing a cell, it stops and
    outputs a traceback.
    '''
    with open(notebook_filename) as f:
        nb = nbformat.read(f, as_version=4)
    path = Path(notebook_filename).resolve()
    notebook_filename_out = tmp_path / f"{path.stem}_converted{path.suffix}"

    skip_cells = TagRemovePreprocessor(remove_cell_tags=("skip-execution",))
    skip_cells.preprocess(nb, {})

    ep = ExecutePreprocessor(timeout=2400, kernel_name="python3")
    try:
        ep.preprocess(nb, {"metadata": {"path": str(path.parent)}})
    except CellExecutionError:
        msg = 'Error executing the notebook "%s".\n\n' % notebook_filename
        msg += 'See notebook "%s" for the traceback.' % notebook_filename_out
        print(msg)
        raise
    finally:
        with open(notebook_filename_out, mode="w", encoding="utf-8") as f:
            nbformat.write(nb, f)


@pytest.mark.parametrize("notebook_filename", recipe_notebooks(), ids=str)
def test_recipe_notebooks(notebook_filename, tmp_path):
    run_notebook(notebook_filename, tmp_path)
