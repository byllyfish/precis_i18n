#!/bin/bash
#
# Submit package to pypi.

set -e

PYPI="${1:-pypitest}"

# Make sure we are in the correct directory.
if [ ! -f "setup.py" ]; then
  echo "Can't find setup.py. Check current working directory."
  exit 1
fi

# Verify long_description.rst is newer than README.md
if [ README.md -nt long_description.rst ]; then
    echo "Must fix: pandoc README.md -o long_description.rst"
fi

echo "Remove old files:" build dist *.egg-info
rm -rf build dist *.egg-info

echo "Build source distribution"
python3.5 setup.py sdist

echo "Build wheel"
python3.5 setup.py bdist_wheel

# Uncomment to register module.
#twine register -r "$PYPI" dist/*.whl

echo "Upload to $PYPI"
twine upload -r "$PYPI" dist/*

exit 0
