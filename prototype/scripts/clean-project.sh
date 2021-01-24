#!/bin/bash
# Remove intermediate and temporary files from the project directory.
# Call from the project root directory in order to delete all respective files.

find . -name "*.py[co]" -delete
find . -name '__pycache__' -delete
find . -name '.ipynb_checkpoints' -exec rm -fr '{}' \;
