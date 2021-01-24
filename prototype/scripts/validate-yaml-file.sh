#!/bin/bash
# Validate the given yaml file via python.
# Requires Python and the Python package pyyaml to be available.
#
# Consider using the tool yamllint https://github.com/adrienverge/yamllint.
#
# based on:
# https://stackoverflow.com/questions/3971822/how-do-i-validate-my-yaml-file-from-command-line

python -c 'import sys, yaml; yaml.safe_load(sys.stdin); print("Yaml valid")' < "$1"
