#!/bin/bash
# Set up a `Wealth` workspace under the given path,
# create a virtual environment,
# download the dependencies
# and copy notebook templates, configurations, sample-data and scripts from the project directory to
# the workspace directory.
# Also, when --dev is specified, install additional development-dependencies.
#
# Call this script from the project's root directory in order to work correctly.
#
# Usage:
#   bash create-workspace.sh [--dev] [<path/to/workspace>]
set -e

default_workspace_dir="${HOME}/wealth/workspace"

show_help() {
    script_name="${0##*/}"

    msg="${script_name}\n"
    msg+="Create a Wealth project workspace.\n"
    msg+="\n"
    msg+="Usage:\n"
    msg+="  ${script_name} [<path>]\n"
    msg+="\n"
    msg+="Examples:\n"
    msg+="  ${script_name}                      # Create a project under ${default_workspace_dir}\n"
    msg+="  ${script_name} ~/stuff/finance      # Create a project under ~/stuff/finance\n"
    # shellcheck disable=SC2059
    printf "$msg"
}

# parse command line options
while [ "$#" -gt 0 ]; do
    case "$1" in
    --dev)
        install_dev_packages=true
        ;;
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        workspace_dir="$1"
        ;;
    esac
    shift
done
workspace_dir="${workspace_dir:-${default_workspace_dir}}"

command -v python3 >/dev/null || { printf 'Error: Python >=3.9 must be available\n'; exit 1; }

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
    || { printf "Python version should be at least ${min_python_version}\n"; exit 2; }

# create workspace directory
[ -e "${workspace_dir}" ] && { printf "Error: ${workspace_dir} already exists.\n"; exit 3; }
mkdir -p "$workspace_dir"
printf 'Installing workspace to: %s\n' "$workspace_dir"

# install Python packages and Jupyter extensions
python3 -m venv "${workspace_dir}/.venv"
# shellcheck disable=SC1090
source "${workspace_dir}/.venv/bin/activate"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pip install --upgrade pip
pip install --upgrade -r "${script_dir}/../requirements.txt"
[ "$install_dev_packages" == true ] \
    && pip install --upgrade -r "${script_dir}/../requirements-dev.txt"
pip freeze > "${workspace_dir}/requirements.txt"
jupyter nbextension enable --py widgetsnbextension --sys-prefix
jupyter labextension install @jupyter-widgets/jupyterlab-manager
deactivate

# copy folders into workspace directory
cp --recursive prototype/* "$workspace_dir"
