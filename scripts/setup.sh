#!/bin/bash
# Set up the Python project for local development.
# Set up a Python virtual environment and install the dependencies.
#
# Usage:
#
#   scripts/setup.sh [--dev] [--clean]
#
# Examples:
#
#   scripts/setup.sh               # set up the project
#   scripts/setup.sh --dev         # set up the project including development packages
#   scripts/setup.sh --clean       # clean already existing artifacts and set up the project
#   scripts/setup.sh --dev --clean # clean artifacts and set the project up for development
set -e

cd "$(dirname "${BASH_SOURCE[0]}")/.."

check_semver_le() {
    # Check whether the first given semantic version is less than or equal to the
    # second given semantic version.
    #
    # Usage:
    #   check_semver_le 3.8 3.9    # returns true
    #   check_semver_le 3.8 3.8    # returns true
    #   check_semver_le 3.8.1 3.8  # returns false
    #   check_semver_le 4 3.1.2    # returns false
    [ "$1" = "$(printf "%s\n%s" "$1" "$2" | sort -V | head -n1)" ]
}

min_python_version='3.9'
python_version="$(python -c "from sys import version_info as i; print(f'{i.major}.{i.minor}')")"
check_semver_le "$min_python_version" "$python_version" \
    || { >&2 echo "Error: Python version should be at least ${min_python_version}."; exit 1; }

[[ "$*" =~ '--clean' ]] && rm -fr .venv/

python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

pip install --upgrade pip
pip install --upgrade -r requirements.txt

[[ "$*" =~ '--dev' ]] && pip install --upgrade -r requirements-dev.txt
