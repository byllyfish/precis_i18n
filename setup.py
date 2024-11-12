"""A setuptools based setup module for precis_i18n.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import re
from os import path

# Always prefer setuptools over distutils
from setuptools import setup

here = path.abspath(path.dirname(__file__))
description_path = path.join(here, "README.md")
version_path = path.join(here, "precis_i18n", "__init__.py")

# Read README.md.
with open(description_path, encoding="utf-8") as f:
    long_description = f.read()

# Extract version number.
with open(version_path, encoding="utf-8") as f:
    version_regex = re.compile(r'(?m)__version__\s*=\s*"(\d+\.\d+\.\d+)"')
    version = version_regex.search(f.read()).group(1)


setup(
    name="precis_i18n",
    packages=["precis_i18n"],
    version=version,
    license="MIT",
    description="PRECIS-i18n: Internationalized Usernames and Passwords",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="precis codec username password",
    # The project's main homepage and author.
    url="https://github.com/byllyfish/precis_i18n",
    author="William W. Fisher",
    author_email="william.w.fisher@gmail.com",
    package_data={
        "precis_i18n": ["py.typed", "*.pyi"],
    },
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Internationalization",
    ],
    zip_safe=True,
)
