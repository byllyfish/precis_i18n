"""A setuptools based setup module for precis_codec.
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
with open(path.join(here, 'precis_codec/__init__.py'), encoding='utf-8') as f:
    version_regex = re.compile(r"(?m)__version__\s*=\s*'(\d+\.\d+\.\d+)'")
    version = version_regex.search(f.read())[1]

setup(
    name='precis_codec',
    packages=['precis_codec'],
    version=version,
    license='MIT',

    description='PRECIS Codec: Internationalized Usernames and Passwords',
    long_description=long_description,
    keywords='precis i18n username password',

    # The project's main homepage and author.
    url='https://github.com/byllyfish/precis_codec',
    author='William W. Fisher',
    author_email='william.w.fisher@gmail.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        #'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    zip_safe=True,
)
