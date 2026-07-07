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


NOTEBOOKS = recipe_notebooks()
NOTEBOOK_COUNT = len(NOTEBOOKS)


def pytest_report_header(config):
    lines = [f"Recipe notebook test plan: {NOTEBOOK_COUNT} notebooks"]
    lines.extend(
        f"  {index}/{NOTEBOOK_COUNT} {notebook}"
        for index, notebook in enumerate(NOTEBOOKS, start=1)
    )
    return lines


def notebook_cases():
    return [
        pytest.param(index, NOTEBOOK_COUNT, notebook, id=str(notebook))
        for index, notebook in enumerate(NOTEBOOKS, start=1)
    ]


def run_notebook(notebook_filename, tmp_path, notebook_index, notebook_count):
    '''
    Reads a notebook from a file, executes it, then writes the result back to a
    temporary file. If an error occurs while executing a cell, it stops and
    outputs a traceback.
    '''
    print(
        f"Notebook {notebook_index}/{notebook_count}: Running {notebook_filename}",
        flush=True,
    )

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
        print(msg, flush=True)
        raise
    finally:
        with open(notebook_filename_out, mode="w", encoding="utf-8") as f:
            nbformat.write(nb, f)

    print(
        f"Notebook {notebook_index}/{notebook_count}: Successfully ran {notebook_filename}",
        flush=True,
    )


@pytest.mark.parametrize(("notebook_index", "notebook_count", "notebook_filename"), notebook_cases())
def test_recipe_notebooks(notebook_index, notebook_count, notebook_filename, tmp_path):
    run_notebook(notebook_filename, tmp_path, notebook_index, notebook_count)
