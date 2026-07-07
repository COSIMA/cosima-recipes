import os
import re
import time
from contextlib import contextmanager
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
ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
SUMMARY_TRACEBACK_LINES = 12


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
RESULTS = []


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


def format_table(rows):
    headers = ("#", "Status", "Time", "Notebook")
    widths = [len(header) for header in headers]
    for row in rows:
        values = (str(row["index"]), row["status"], f'{row["seconds"]:.1f}s', str(row["notebook"]))
        widths = [max(width, len(value)) for width, value in zip(widths, values)]

    def render(values):
        return " | ".join(str(value).ljust(width) for value, width in zip(values, widths))

    separator = "-+-".join("-" * width for width in widths)
    lines = [render(headers), separator]
    for row in rows:
        lines.append(
            render((str(row["index"]), row["status"], f'{row["seconds"]:.1f}s', str(row["notebook"])))
        )
    return lines


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not RESULTS:
        return

    total = len(RESULTS)
    passed = sum(row["status"] == "PASS" for row in RESULTS)
    failed = sum(row["status"] == "FAIL" for row in RESULTS)

    terminalreporter.write_sep("=", "Recipe notebook summary")
    for line in format_table(RESULTS):
        terminalreporter.write_line(line)
    terminalreporter.write_line(f"Total: {total} | Success: {passed} | Fail: {failed}")


@contextmanager
def redirect_stderr_to(path):
    original_stderr_fd = os.dup(2)
    try:
        with open(path, "ab", buffering=0) as stderr_file:
            os.dup2(stderr_file.fileno(), 2)
            yield
    finally:
        os.dup2(original_stderr_fd, 2)
        os.close(original_stderr_fd)


def strip_ansi(text):
    return ANSI_ESCAPE.sub("", text)


def compact_traceback(traceback):
    lines = []
    for line in traceback:
        lines.extend(strip_ansi(line).splitlines())
    lines = [line for line in lines if line.strip()]
    return "\n".join(lines[-SUMMARY_TRACEBACK_LINES:])


def notebook_error_summary(nb):
    for cell_index, cell in enumerate(nb.cells, start=1):
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                ename = strip_ansi(output.get("ename", "Error"))
                evalue = strip_ansi(output.get("evalue", ""))
                traceback = compact_traceback(output.get("traceback", []))
                lines = [f"Cell {cell_index}: {ename}: {evalue}"]
                if traceback:
                    lines.extend(("Traceback excerpt:", traceback))
                return "\n".join(lines)

    return "No error output was captured in the executed notebook."


def run_notebook(notebook_filename, tmp_path, notebook_index, notebook_count):
    '''
    Reads a notebook from a file, executes it, then writes the result back to a
    temporary file. If an error occurs while executing a cell, it returns a
    concise failure report instead of dumping noisy child-process tracebacks.
    '''
    start = time.monotonic()
    print(
        f"\nNotebook {notebook_index}/{notebook_count}: Running {notebook_filename}",
        flush=True,
    )

    with open(notebook_filename) as f:
        nb = nbformat.read(f, as_version=4)
    path = Path(notebook_filename).resolve()
    notebook_filename_out = tmp_path / f"{path.stem}_converted{path.suffix}"
    stderr_log = tmp_path / f"{path.stem}_stderr.log"

    skip_cells = TagRemovePreprocessor(remove_cell_tags=("skip-execution",))
    skip_cells.preprocess(nb, {})

    ep = ExecutePreprocessor(timeout=2400, kernel_name="python3")
    failure = None
    try:
        with redirect_stderr_to(stderr_log):
            ep.preprocess(nb, {"metadata": {"path": str(path.parent)}})
    except CellExecutionError:
        failure = notebook_error_summary(nb)
    except Exception as exc:
        failure = f"Notebook executor failed before a cell error was captured: {type(exc).__name__}: {exc}"
    finally:
        with open(notebook_filename_out, mode="w", encoding="utf-8") as f:
            nbformat.write(nb, f)

    seconds = time.monotonic() - start

    if failure is not None:
        RESULTS.append({"index": notebook_index, "status": "FAIL", "seconds": seconds, "notebook": notebook_filename})
        stderr_size = stderr_log.stat().st_size if stderr_log.exists() else 0
        message = "\n".join(
            (
                f"Notebook {notebook_index}/{notebook_count}: FAILED {notebook_filename}",
                failure,
                f"Converted notebook: {notebook_filename_out}",
                f"Suppressed stderr log: {stderr_log} ({stderr_size} bytes)",
            )
        )
        print(message, flush=True)
        return message

    RESULTS.append({"index": notebook_index, "status": "PASS", "seconds": seconds, "notebook": notebook_filename})
    print(
        f"Notebook {notebook_index}/{notebook_count}: Successfully ran {notebook_filename}",
        flush=True,
    )
    return None


@pytest.mark.parametrize(("notebook_index", "notebook_count", "notebook_filename"), notebook_cases())
def test_recipe_notebooks(notebook_index, notebook_count, notebook_filename, tmp_path):
    failure = run_notebook(notebook_filename, tmp_path, notebook_index, notebook_count)
    if failure is not None:
        pytest.fail(failure, pytrace=False)
