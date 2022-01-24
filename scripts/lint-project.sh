#!/bin/bash
# Run linters with the project's preferences.
# Runs the tools Flake8, Pylint, Mypy, Black, Isort, Vulture and Shellcheck one after another.
# Run the script with an active, viable virtualenv from the project's root directory.

lint_python_files() {
    # Lint the given python file or lont all Python files under the given folder.
    path="$1"
    printf -- '\e[1mFlake8...\e[0m\n'
    flake8 "$path"

    printf -- '\e[1mPylint...\e[0m\n'
    pylint "$path" --msg-template='{path}:{line}: {msg_id} {symbol} {msg}' --score no

    printf -- '\e[1mMypy...\e[0m\n'
    mypy \
        --follow-imports=skip \
        --ignore-missing-imports \
        --no-color-output \
        --no-error-summary \
        --show-error-codes \
        "$path"

    printf -- '\e[1mBlack...\e[0m\n'
    black --check --quiet "$path" || printf 'The black formatting is bad\n'

    printf -- '\e[1mIsort...\e[0m\n'
    isort --profile black --check-only --diff "$path"

    printf -- '\e[1mVulture...\e[0m\n'
    vulture --min-confidence 100 "$path"
}

root_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../src/"

printf '\e[1msetup.py...\e[0m\n'
lint_python_files "$root_path/setup.py"

printf '\e[1mOther Python code...\e[0m\n'
lint_python_files "$root_path/wealth/"

printf -- '\e[1mShellcheck...\e[0m\n'
shellcheck_exclude_codes_array=(
    'SC1090'  # Can't follow non-constant source
)
shellcheck_exclude_codes="$(printf '%s,' "${shellcheck_exclude_codes_array[@]}")"
find "scripts" -iname "*.sh" -exec shellcheck --exclude "$shellcheck_exclude_codes" '{}' \;
