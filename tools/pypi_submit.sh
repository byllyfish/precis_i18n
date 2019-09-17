#!/bin/bash
#
# Submit package to pypi.
# 
# Usage:
#    ./tools/pypi_submit.sh pypi
#
# Requires:   setuptools wheel twine

set -e

PYPI="${1:-pypitest}"
GPG_KEY="F0BB53DAD0664BD49C6C2304A0BC617BBE7CC332"

# Make sure we are in the correct directory.
if [ ! -f "setup.py" ]; then
  echo "Can't find setup.py. Check current working directory."
  exit 1
fi

echo "Remove old files:" build dist *.egg-info
rm -rf build dist *.egg-info

echo "Build source distribution"
python3 setup.py sdist

echo "Build wheel"
python3 setup.py bdist_wheel

#echo "Sign packages"
#gpg -u $GPG_KEY --detach-sign -a dist/*.whl
#gpg -u $GPG_KEY --detach-sign -a dist/*.gz

# Uncomment to register module.
#twine register -r "$PYPI" dist/*.whl

echo "Upload to $PYPI"
twine upload --verbose -r "$PYPI" -s -i $GPG_KEY dist/*

exit 0
