import os
import sys
import unittest

from precis_i18n.derived import derived_property
from precis_i18n.unicode import UnicodeData

try:
    import unicodedata2
except ImportError:
    unicodedata2 = None


class TestDerivedProperties(unittest.TestCase):
    """ Test output of derived_property function.
    """
    def test_derived_props(self):
        """ Compare derived properties against a "golden" file using built-in
        unicodedata module.
        """
        self._test_derived_props(UnicodeData())

    @unittest.skipIf(unicodedata2 is None, 'unicodedata2 not available')
    def test_derived_props_unicodedata2(self):
        """ Compare derived properties against a "golden" file using
        pip-installed unicodedata2 module.
        """

        ucd = UnicodeData(unicodedata2)
        assert ucd.version == 12.0
        self._test_derived_props(ucd)

    def _test_derived_props(self, ucd):
        """ Compare derived properties against a "golden" file.
        """

        goldname = 'derived-props-%.1f.txt' % ucd.version
        goldpath = os.path.join(os.path.dirname(__file__), goldname)

        with open(goldpath) as golden:
            derived_props = enumerate_derived_props(ucd)
            for line in golden:
                line = line.strip()
                if not line:
                    continue
                expected = '%04X-%04X %s' % next(derived_props)
                self.assertEqual(line, expected)


def enumerate_derived_props(ucd, begin=0, end=0x00110000):
    """ Iterable producing all derived_property values for a particular range.

    Produces a sequence of tuples (begin, end, property).
    """
    start = begin
    prev = '/'.join(derived_property(start, ucd))
    for cp in range(start + 1, end):
        prop = '/'.join(derived_property(cp, ucd))
        if prop != prev:
            yield (start, cp - 1, prev)
            start = cp
            prev = prop
    yield (start, cp, prev)


def main():
    ucd = UnicodeData()
    print('Unicode %.1f' % ucd.version, file=sys.stderr)
    # Dump gold file to stdout.
    for p in enumerate_derived_props(ucd):
        print('%04X-%04X %s' % p)


if __name__ == '__main__':
    main()
