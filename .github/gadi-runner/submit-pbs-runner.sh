#!/usr/bin/env bash
set -euo pipefail

REPO_CHECKOUT="${GITHUB_RUNNER_REPO:-/g/data/v46/txs156/cosima-recipes}"
RUNNER_ROOT="${GITHUB_RUNNER_ROOT:-/g/data/v46/txs156/actions-runner/cosima-recipes-gadi}"
RESUBMIT="${GITHUB_RUNNER_RESUBMIT:-0}"

cd "${REPO_CHECKOUT}"
GITHUB_RUNNER_ROOT="${RUNNER_ROOT}" GITHUB_RUNNER_REPO="${REPO_CHECKOUT}" GITHUB_RUNNER_RESUBMIT="${RESUBMIT}" qsub .github/gadi-runner/runner.pbs
