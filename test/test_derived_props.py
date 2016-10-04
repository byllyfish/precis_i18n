import unittest
import os
import sys
from precis_i18n.derived import derived_property
from precis_i18n.unicode import UnicodeData


UCD = UnicodeData()
GOLDNAME = 'derived-props-%.1f.txt' % UCD.version
GOLDPATH = os.path.join(os.path.dirname(__file__), GOLDNAME)


class TestDerivedProperties(unittest.TestCase):
    """ Test output of derived_property function.
    """

    def test_derived_props(self):
        """ Compare derived properties against a "golden" file.
        """

        with open(GOLDPATH) as golden:
            derived_props = enumerate_derived_props()
            for line in golden:
                line = line.strip()
                if not line:
                    continue
                expected = '%04X-%04X %s' % next(derived_props)
                self.assertEqual(line, expected)


def enumerate_derived_props(begin=0, end=0x00110000):
    """ Iterable producing all derived_property values for a particular range.

    Produces a sequence of tuples (begin, end, property).
    """
    start = begin
    prev = '/'.join(derived_property(start, UCD))
    for cp in range(start + 1, end):
        prop = '/'.join(derived_property(cp, UCD))
        if prop != prev:
            yield (start, cp-1, prev)
            start = cp
            prev = prop
    yield (start, cp, prev)


if __name__ == '__main__':
    print('Unicode %.1f' % UCD.version, file=sys.stderr)
    # Dump gold file to stdout.
    for p in enumerate_derived_props():
        print('%04X-%04X %s' % p)
