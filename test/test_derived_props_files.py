import unittest
import os
import re

VERSIONS = [
    '6.1', '6.2', '6.3', '8.0', '9.0', '10.0', '11.0', '12.0', '12.1', '13.0'
]

UNASSIGNED = 1

PROPS = {
    'UNASSIGNED': UNASSIGNED,
    'PVALID': 2,
    'FREE_PVAL': 3,
    'ID_DIS or FREE_PVAL': 3,  # found in IANA format only
    'DISALLOWED': 4,
    'CONTEXTJ': 5,
    'CONTEXTO': 6
}

LINE_REGEX = re.compile(
    r'^([0-9A-F]{4,6})-([0-9A-F]{4,6}) ([A-Z_]+)/[a-z0-9_]+$')

IANA_LINE_REGEX = re.compile(r'^([0-9A-F]{4,6})(-[0-9A-F]{4,6})?,([^,]+),.+$')

DIR_PATH = os.path.dirname(__file__)

# Allowed transitions between two versions V1 -> V2 for specific code points.
EXCEPTIONS = {
    0x111c9: (PROPS['FREE_PVAL'], PROPS['PVALID'])  # SHARADA SANDHI MARK
}


def _allowed_change(cp, tbl1, tbl2):
    """Return true if the transition is allowed.

    We allow changing from UNASSIGNED to anything. Also, in 10.0 -> 11.0, the
    code point 70089 (0x111c9, SHARADA SANDHI MARK) changed from FREE_PVAL to 
    PVALID.
    """
    if tbl1 == UNASSIGNED:
        return True
    rule = EXCEPTIONS.get(cp)
    if rule:
        return (tbl1, tbl2) == rule
    return False


def _load_table(filename):
    """Load data from `derived-props-<version>.txt` file."""

    table = bytearray(0x110000)

    with open(filename) as fp:
        for line in fp:
            m = LINE_REGEX.match(line)
            assert m, 'Unexpected format: %s' % line

            lo, hi = int(m.group(1), 16), int(m.group(2), 16)
            prop = PROPS[m.group(3)]
            for cp in range(lo, hi + 1):
                table[cp] = prop

    # Check that all codepoints are assigned.
    for cp in range(0x110000):
        assert table[cp] != 0, 'Codepoint missing: %d' % cp

    return table


def _load_table_iana(filename):
    """Load table from IANA csv file."""

    table = bytearray(0x110000)

    with open(filename) as fp:
        for line in fp:
            # Ignore csv header.
            if line == 'Codepoint,Property,Description\n':
                continue

            m = IANA_LINE_REGEX.match(line)
            assert m, 'Unexpected format: %s' % line

            lo = int(m.group(1), 16)
            if m.group(2):
                hi = int(m.group(2)[1:], 16)
            else:
                hi = lo

            prop = PROPS[m.group(3)]
            for cp in range(lo, hi + 1):
                table[cp] = prop

    # Check that all codepoints are assigned.
    for cp in range(0x110000):
        assert table[cp] != 0, 'Codepoint missing: %d' % cp

    return table


def _load_tables():
    """Load data from all derived-props files."""

    tables = []
    file_template = os.path.join(DIR_PATH, 'derived-props-%s.txt')

    for version in VERSIONS:
        table = _load_table(file_template % version)
        tables.append((version, table))

    return tables


class TestDerivedPropsFiles(unittest.TestCase):
    def test_derived_props(self):
        """Check derived property values do not change as UCD version increases.

        The only allowed change is from UNASSIGNED to anything.
        """
        tables = _load_tables()

        for i in range(len(tables) - 1):
            # Compare table i to table i+1.
            # If table[i] != table[i+1] then table[i] must equal UNASSIGNED(1).
            ver1, tbl1 = tables[i]
            ver2, tbl2 = tables[i + 1]
            for j in range(0x110000):
                if not _allowed_change(j, tbl1[j], tbl2[j]):
                    self.assertEqual(tbl1[j], tbl2[j],
                                     'cp = %d (%s -> %s)' % (j, ver1, ver2))

    def test_iana_derived_props(self):
        """Compare IANA precis-tables to derived-props-6.3.txt"""

        iana_path = os.path.join(DIR_PATH, 'iana-precis-tables-6.3.0.csv')
        test_path = os.path.join(DIR_PATH, 'derived-props-6.3.txt')

        iana_table = _load_table_iana(iana_path)
        table = _load_table(test_path)

        # Tables should be identical.
        self.assertTrue(table == iana_table)
