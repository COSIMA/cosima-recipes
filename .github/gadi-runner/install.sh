#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${GITHUB_REPOSITORY_URL:-https://github.com/COSIMA/cosima-recipes}"
RUNNER_ROOT="${GITHUB_RUNNER_ROOT:-${HOME}/actions-runner/cosima-recipes-gadi}"
RUNNER_NAME="${GITHUB_RUNNER_NAME:-$(hostname -s)-cosima-recipes}"
RUNNER_LABELS="${GITHUB_RUNNER_LABELS:-gadi,linux}"
RUNNER_WORK="${GITHUB_RUNNER_WORK:-_work}"
RUNNER_VERSION="${GITHUB_RUNNER_VERSION:-}"
RUNNER_TOKEN="${GITHUB_RUNNER_TOKEN:-}"

if [ -z "${RUNNER_TOKEN}" ]; then
  cat >&2 <<'MSG'
GITHUB_RUNNER_TOKEN is required.

Create one in GitHub:
  COSIMA/cosima-recipes -> Settings -> Actions -> Runners -> New self-hosted runner -> Linux x64

Then rerun, for example:
  GITHUB_RUNNER_TOKEN=... .github/gadi-runner/install.sh
MSG
  exit 2
fi

if [ -z "${RUNNER_VERSION}" ]; then
  RUNNER_VERSION="$(${PYTHON:-python3} - <<'PYV'
import json
import urllib.request

with urllib.request.urlopen("https://api.github.com/repos/actions/runner/releases/latest") as response:
    release = json.load(response)
print(release["tag_name"].lstrip("v"))
PYV
)"
fi

case "$(uname -m)" in
  x86_64) runner_arch=x64 ;;
  aarch64|arm64) runner_arch=arm64 ;;
  *) echo "Unsupported runner architecture: $(uname -m)" >&2; exit 2 ;;
esac

archive="actions-runner-linux-${runner_arch}-${RUNNER_VERSION}.tar.gz"
download_url="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${archive}"

mkdir -p "${RUNNER_ROOT}"
cd "${RUNNER_ROOT}"

if [ ! -x ./config.sh ]; then
  echo "Downloading ${download_url}"
  curl -fsSL -o "${archive}" "${download_url}"
  tar xzf "${archive}"
fi

./config.sh   --url "${REPO_URL}"   --token "${RUNNER_TOKEN}"   --name "${RUNNER_NAME}"   --labels "${RUNNER_LABELS}"   --work "${RUNNER_WORK}"   --unattended   --replace

cat <<MSG

Runner configured in ${RUNNER_ROOT}.

Start it with:
  cd ${RUNNER_ROOT}
  ./run.sh

The Recipe Tests workflow requires a runner with these labels:
  self-hosted, linux, gadi
MSG
