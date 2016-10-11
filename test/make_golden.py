#!/bin/env python3
#
# Take a source file as input and produce a json file.
#
#  make_golden.py < golden_source.txt > golden.json
#

import json
import sys
import precis_i18n.codec
from collections import OrderedDict


PROFILES = ['UsernameCasePreserved', 'UsernameCaseMapped', 'OpaqueString', 'Nickname']


def _unescape(value):
    """ Unescape escapes in a python string.

    Examples:   \xFF \uFFFF \U0010FFFF \\ \n \t \r
    """
    return value.encode('ascii').decode('unicode_escape')


def main():
    """ Produce golden.json file from list of inputs.
    """

    # Read list of inputs from ASCII file, and unescape them.
    inputs = ['', '#']
    for line in sys.stdin:
        data = _unescape(line.strip())
        if not data or data[0] == '#':
            continue
        inputs.append(data)

    # For each profile, test all the inputs and produce a list of result
    # objects.
    results = []
    for profile in PROFILES:
        for data in inputs:
            try:
                output = data.encode(profile).decode('utf-8')
                reason = None
            except UnicodeEncodeError as ex:
                output = None
                reason = ex.reason
            results.append(OrderedDict([('profile', profile), 
                                        ('input', data), 
                                        ('output', output), 
                                        ('error', reason)]))

    # Save results as a JSON file.
    json.dump(results, sys.stdout, indent=2, ensure_ascii=True)


if __name__ == '__main__':
    main()
    
