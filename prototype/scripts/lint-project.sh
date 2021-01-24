#!/bin/bash
# Run linters with the project's preferences.
# In order for the script to work correctly, run it from the project's root directory.

printf -- '\e[1mFlake8...\e[0m\n'
flake8_error_codes_array=(
    'E128'  # continuation line under-indented for visual indent
    'E501'  # line too long (87 > 79 characters)
    'E712'  # comparison to False should be 'if cond is False:' or 'if not cond:'
    'W504'  # line break after binary operator
)
flake8_error_codes="$(printf '%s,' "${flake8_error_codes_array[@]}")"
find src/ -iname "*.py" -exec flake8 --ignore="$flake8_error_codes" '{}' \;

printf -- '\e[1mPylint...\e[0m\n'
pylint_error_codes_array=(
    'C0103'  # does not conform to snake case style
    'C0121'  # Comparison to False should be 'not expr' or 'expr is False'
    'C0330'  # Wrong continued indentation (add 2 spaces).
    'C0412'  # Imports from package matplotlib are not grouped
    'E0401'  # unable to import foo.bar
    'R0903'  # too few public methods
    'R0913'  # too many arguments
    'R0914'  # too many local variables
)
pylint_error_codes="$(printf '%s,' "${pylint_error_codes_array[@]}")"
find src/ -iname "*.py" -exec \
    pylint --disable="$pylint_error_codes" --msg-template='{msg_id} {path}:{line}: {msg}' '{}' \;

printf -- '\e[1mShellcheck...\e[0m\n'
shellcheck_exclude_codes_array=(
    'SC1090'  # Can't follow non-constant source
)
shellcheck_exclude_codes="$(printf '%s,' "${shellcheck_exclude_codes_array[@]}")"
find scripts/ -iname "*.sh" -exec \
    shellcheck --exclude "$shellcheck_exclude_codes" '{}' \;
