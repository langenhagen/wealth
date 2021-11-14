#!/bin/bash
# Run linters with the project's preferences.
# Make sure that the linters flake8, pylint, mypy and shellcheck are available on your system.
# Run the script with an active, viable virtualenv from the project's root directory.
# In order for the script to work correctly, run it from the project's root directory.

root_path="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../src"

printf -- '\e[1mFlake8...\e[0m\n'
flake8 "$root_path"

printf -- '\e[1mPylint...\e[0m\n'
pylint "$root_path" --msg-template='{msg_id} {path}:{line}: {msg}' --score no

printf -- '\e[1mMypy...\e[0m\n'
mypy --ignore-missing-imports --follow-imports=skip --no-color-output --no-error-summary "$root_path"

printf -- '\e[1mBlack...\e[0m\n'
black --check --quiet "$root_path" || printf 'The black formatting is bad\n'

printf -- '\e[1mIsort...\e[0m\n'
isort --profile black --check-only --diff "$root_path"

printf -- '\e[1mShellcheck...\e[0m\n'
shellcheck_exclude_codes_array=(
    'SC1090'  # Can't follow non-constant source
)
shellcheck_exclude_codes="$(printf '%s,' "${shellcheck_exclude_codes_array[@]}")"
find "scripts" -iname "*.sh" -exec shellcheck --exclude "$shellcheck_exclude_codes" '{}' \;
