#!/bin/bash
# Run linters with the project's preferences.
# Make sure that the linters flake8, pylint, mypy and shellcheck are available on your system.
# Run the script with an active, viable virtualenv from the project's root directory.
# In order for the script to work correctly, run it from the project's root directory.

root_path='src'

printf -- '\e[1mFlake8...\e[0m\n'
flake8_error_codes_array=(
    'E128'  # continuation line under-indented for visual indent
    'E501'  # line too long (87 > 79 characters)
    'E712'  # comparison to False should be 'if cond is False:' or 'if not cond:'
    'W503'  # line break after binary operator
)
flake8_error_codes="$(printf '%s,' "${flake8_error_codes_array[@]}")"
find "$root_path" -iname "*.py" -exec \
    flake8 --ignore="$flake8_error_codes" '{}' \;

printf -- '\e[1mPylint...\e[0m\n'
pylint_error_codes_array=(
    'C0103'  # Does not conform to snake case style
    'C0121'  # Comparison to False should be 'not expr' or 'expr is False'
    'C0330'  # Wrong continued indentation (add 2 spaces).
    'C0412'  # Imports from package matplotlib are not grouped
    'E0401'  # Unable to import foo.bar
    'R0903'  # Too few public methods
    'R0913'  # Too many arguments
    'R0914'  # Too many local variables
    'W0603'  # Using the global statement
    'W1203'  # Use lazy % formatting in logging functions

)
pylint_error_codes="$(printf '%s,' "${pylint_error_codes_array[@]}")"
find "$root_path" -iname "*.py" -exec \
    pylint \
        --disable="$pylint_error_codes" \
        --msg-template='{msg_id} {path}:{line}: {msg}' '{}' \
        --score no \;

printf -- '\e[1mmypy...\e[0m\n'
find "$root_path" -iname "*.py" -exec \
    mypy --ignore-missing-imports --follow-imports=skip --no-color-output --no-error-summary '{}' \;

printf -- '\e[1mShellcheck...\e[0m\n'
shellcheck_exclude_codes_array=(
    'SC1090'  # Can't follow non-constant source
)
shellcheck_exclude_codes="$(printf '%s,' "${shellcheck_exclude_codes_array[@]}")"
find "scripts" -iname "*.sh" -exec \
    shellcheck --exclude "$shellcheck_exclude_codes" '{}' \;
