# Gadi GitHub Actions runner

The recipe notebook workflow cannot run on GitHub-hosted runners because it needs NCI storage and the `conda/analysis3` module under `/g/data/xp65/public/modules`. A GitHub self-hosted runner must be registered on a Gadi-accessible host and labelled `gadi` and `linux`.

## One-time setup

From a Gadi host that is allowed to run a lightweight long-lived process and can access GitHub:

```bash
cd /g/data/v46/txs156/cosima-recipes
GITHUB_RUNNER_TOKEN=... .github/gadi-runner/install.sh
```

Create `GITHUB_RUNNER_TOKEN` in GitHub:

```text
COSIMA/cosima-recipes -> Settings -> Actions -> Runners -> New self-hosted runner -> Linux x64
```

The script installs the runner into:

```text
$HOME/actions-runner/cosima-recipes-gadi
```

Override this with `GITHUB_RUNNER_ROOT=/path/to/runner` if needed.

## Start the runner

```bash
.github/gadi-runner/run.sh
```

For unattended operation, start that command under whatever process supervisor is appropriate for the host. The runner must remain online for GitHub to dispatch PR checks to it.

## Required labels

The workflow uses:

```yaml
runs-on: [self-hosted, linux, gadi]
```

The installer adds `gadi,linux`; GitHub automatically adds `self-hosted`.

## What the workflow does

Once GitHub dispatches the job to this runner, `.github/workflows/recipe-tests.yml` submits the actual notebook test workload to PBS, loads:

```bash
module use /g/data/xp65/public/modules
module load conda/analysis3
```

and runs:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -ra test/test_notebooks.py
```

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` avoids unrelated third-party pytest plugin entry point failures in `conda/analysis3`.

## Cleanup

To remove the runner registration:

```bash
cd $HOME/actions-runner/cosima-recipes-gadi
./config.sh remove --token <remove-token-from-github>
```
