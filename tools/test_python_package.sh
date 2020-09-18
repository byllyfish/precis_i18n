#!/bin/bash
#
# Build source package and test it.

set -e

if [ "$TRAVIS_PYTHON_VERSION" = "pypy3" ]; then
    echo "Skip test of source package on pypy."
    exit 0
fi

python setup.py sdist
cd dist
tar xvfz precis_i18n-*.tar.gz
cd precis_i18n-*
python setup.py test
exit 0
