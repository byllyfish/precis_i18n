"""A setuptools based setup module for precis_i18n.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path
import re

here = path.abspath(path.dirname(__file__))

# Read long_description.rst.
with open(path.join(here, 'long_description.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Extract version number.
with open(path.join(here, 'precis_i18n/__init__.py'), encoding='utf-8') as f:
    version_regex = re.compile(r"(?m)__version__\s*=\s*'(\d+\.\d+\.\d+)'")
    version = version_regex.search(f.read()).group(1)

# Running `python setup.py test` should run unit tests (see `test_suite`).
def all_tests():
    import unittest
    test_loader = unittest.TestLoader()
    return test_loader.discover('test')


setup(
    name='precis_i18n',
    packages=['precis_i18n'],
    version=version,
    license='MIT',

    description='PRECIS-i18n: Internationalized Usernames and Passwords',
    long_description=long_description,
    keywords='precis codec username password',

    # The project's main homepage and author.
    url='https://github.com/byllyfish/precis_i18n',
    author='William W. Fisher',
    author_email='william.w.fisher@gmail.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Internationalization'
    ],

    zip_safe=True,
    test_suite="setup.all_tests"
)
