#!/usr/bin/env bash
set -euo pipefail

RUNNER_ROOT="${GITHUB_RUNNER_ROOT:-/g/data/v46/txs156/actions-runner/cosima-recipes-gadi}"
cd "${RUNNER_ROOT}"
exec ./run.sh
