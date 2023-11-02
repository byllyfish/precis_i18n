#!/bin/env python3
#
# Take a source file as input and produce a json file.
#
#  make_golden.py < golden_source.txt > golden.json
#

import json
import re
import sys
from collections import OrderedDict

import precis_i18n.codec  # noqa: F401

PROFILES = [
    "UsernameCasePreserved",
    "UsernameCaseMapped",
    "OpaqueString",
    "NicknameCaseMapped",
    "UsernameCaseMapped:ToLower",
    "NicknameCasePreserved",
    "NicknameCaseMapped:ToLower",
    "FreeFormClass",
    "IdentifierClass",
    "UsernameCaseMapped:CaseFold",
    "NicknameCaseMapped:CaseFold",
]

_ANY_PROFILE = re.compile(r".")

EXCEPTIONS = {
    # ToLower difference before Unicode 8.0. The lower case characters weren't
    # added until Unicode 8.0.
    "\u13da\u13a2\u13b5\u13ac\u13a2\u13ac\u13d2": [
        (re.compile(r".+CaseMapped(:ToLower)?$"), 8.0)
    ],
    # U+1AB6 was introduced in 7.0.
    "\u05d0\u1ab6\u05d1": [(_ANY_PROFILE, 7.0)],
    # U+0111C9 changed to PVALID in 11.0. It was introduced in 8.0.
    "\U000111c9": [
        (re.compile(r"^(?:Username.*|IdentifierClass)$"), 11.0),
        (_ANY_PROFILE, 8.0),
    ],
    # U+05EF was introduced in 11.0.
    "\u05EF\u05f3": [(_ANY_PROFILE, 11.0)],
    # U+088E, U+0886 were introduced in 14.0.
    "\U00010D00\u200c\u088E": [(_ANY_PROFILE, 14.0)],
    "\U00010D00\u07fd\u200c\u07fd\u088E": [(_ANY_PROFILE, 14.0)],
    "\u0886\u200c\u0886": [(_ANY_PROFILE, 14.0)],
}


def _unescape(value):
    """Unescape escapes in a python string.

    Examples:   \xFF \uFFFF \U0010FFFF \\ \n \t \r
    """
    return value.encode("ascii").decode("unicode_escape")


def main():
    """Produce golden.json file from list of inputs."""

    # Read list of inputs from ASCII file, and unescape them.
    inputs = ["", "#"]
    for line in sys.stdin:
        data = _unescape(line.strip())
        if not data or data[0] == "#":
            continue
        inputs.append(data)

    # For each profile, test all the inputs and produce a list of result
    # objects.
    results = []
    for profile in PROFILES:
        for data in inputs:
            unicode_version = None
            # Skip this profile for certain exceptions.
            if data in EXCEPTIONS:
                for excl in EXCEPTIONS[data]:
                    if excl[0].match(profile):
                        unicode_version = excl[1]
                        break
            try:
                output = data.encode(profile).decode("utf-8")
                reason = None
            except UnicodeEncodeError as ex:
                output = None
                reason = ex.reason
            elem = OrderedDict(
                [
                    ("profile", profile),
                    ("input", data),
                    ("output", output),
                    ("error", reason),
                ]
            )
            if unicode_version is not None:
                elem["unicode_version"] = unicode_version
            results.append(elem)

    # Save results as an ASCII JSON file. Make sure file ends with LF.
    json.dump(results, sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
