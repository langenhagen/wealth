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

die() {
    printf -- '%s\n' "$1"
    exit "${2:-1}"
}

# check if python is available
command -v python3 >/dev/null || die 'Error: Python >=3.7 must be available' 1

# check if Python is available and if version is compatible
available_python_version="$(python3 --version | grep -Eo '[0-9.]+')"
min_required_python_version='3.7.0'
both_versions="$(printf '%s\n%s' "$available_python_version" "$min_required_python_version")"
lower_version="$(printf '%s' "$both_versions" | sort -V | head -1)"
error_msg="Errror: Wealth requires at least Python version ${min_required_python_version}. "
error_msg+="Found Python version ${available_python_version}."
[ "$lower_version" != "$min_required_python_version" ] && die "$error_msg" 2

# create workspace directory
[ -e "${workspace_dir}" ] && die "Error: ${workspace_dir} already exists." 3
mkdir -p "$workspace_dir"
printf 'Installing workspace to: %s\n' "$workspace_dir"

# install Python packages and jupyter extensions
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
