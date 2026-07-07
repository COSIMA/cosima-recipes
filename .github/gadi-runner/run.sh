#!/usr/bin/env bash
set -euo pipefail

RUNNER_ROOT="${GITHUB_RUNNER_ROOT:-${HOME}/actions-runner/cosima-recipes-gadi}"
cd "${RUNNER_ROOT}"
exec ./run.sh
