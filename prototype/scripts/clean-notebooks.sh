#!/bin/bash
# Clean the output and stats from the Jupiter notebooks
# Call from the project root directory in order to clean all notebooks.

find . -iname '*.ipynb' \
    -exec jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace '{}' \;
