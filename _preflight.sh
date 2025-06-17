#!/bin/bash

set -eux -o pipefail

VENV_PATH=${VENV_PATH:-".venv/"}
STRICT_DOCS=${STRICT_DOCS:-"false"}
PROJECT=${PROJECT:-"hondana"}
API_YAML="_api.yaml"
OLD_API_YAML="_api.old.yaml"

die() { echo "$*" 1>&2; exit 1; }

if [[ ! -d "${VENV_PATH}" ]]; then
    die "virtualenvironment does not exist."
fi

# activate the venv to get proper env vars
# shellcheck source=./.venv/bin/activate
source .venv/bin/activate

run_ruff(){
    if ! command -v ruff > /dev/null 2>&1; then
        die "ruff is not installed."
    fi

    if ! ruff check .; then
        die "Ruff check failed."
    fi
    if ! ruff format --check .; then
        die "Ruff format failed."
    fi
}

api_diff(){
    if [[ -f "${API_YAML}" ]]; then
        mv "${API_YAML}" "${OLD_API_YAML}"
    else
        echo "No API file, skipping to downloading new one."
    fi

    curl -SsL "https://api.mangadex.org/docs/static/api.yaml" -o _api.yaml

    if ! cmp -s "${API_YAML}" "${OLD_API_YAML}"; then
        die "There's an API change, check the diff: \`diff ${API_YAML} ${OLD_API_YAML}\`"
    fi
}

preflight_tags() {
    python _preflight.py -t
}

preflight_reports() {
    python _preflight.py -r
}

run_pyright(){
    pyright
    pyright --ignoreexternal --verifytypes "${PROJECT}"
}

build_docs() {
    if [[ "${STRICT_DOCS}" != "false" ]]; then
        sphinx-build -anEWT --keep-going docs/ docs/build
    else
        sphinx-build -aEWT --keep-going docs/ docs/build
    fi
}

run_tests() {
    pytest
}

{
    run_ruff
    api_diff
    preflight_tags
    preflight_reports
    run_pyright
    build_docs
    run_tests
} 2>&1 | tee preflight.log
