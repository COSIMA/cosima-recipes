This folder contains scripts used to run the recipe notebooks and confirm they are still in a working state (using pytest).

The notebook test discovers all notebooks under:

- `01-Cooking-Tutorials`
- `02-Easy-Recipes`
- `03-Advanced-Recipes`
- `04-Regional-Specialties`

On NCI, run the suite with the `conda/analysis3-25.09` module:

```bash
module use /g/data/xp65/public/modules
module load conda/analysis3-25.09
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -s --tb=short -ra test/test_notebooks.py
```

In GitHub Actions, the workflow submits these notebooks as a PBS array job: one array task per notebook, with concurrency controlled by `PBS_ARRAY_CONCURRENCY` in `.github/workflows/recipe-tests.yml`.

For cells in notebooks which are expected to fail, you need to add a 'skip-execution' tag which will cause the cell to be skipped in automated testing.
To do this, select the cell and open the Property Inspector (click on the icon with two cogged wheels on the right of JupyterLab) and add a tag with the text 'skip-execution'.
