"""
Implements the CodepointSet class.
"""

import io
import re
from bisect import bisect_left


class CodepointSet(object):
    """ Concrete class for an immutable set of Unicode code points.

    Inclusive ranges [a, b] are stored as adjacent unicode characters in a
    string. The low end of a range has an even index. The high end is at an
    odd index. Singleton ranges are stored as [c, c].

    To test if a code point is in the set, search for the code point. If it
    matches a char in the string, the code point is in the set. If not, find
    the index of the next largest char. If this index is odd, the code point is
    in the set.
    """

    def __init__(self, table):
        elems = _coalesce(_parse(table))
        self._table = ''.join(chr(lo) + chr(hi) for (lo, hi) in elems)
        assert (len(self._table) % 2) == 0

    def __contains__(self, cp):
        """ Return true if code point `cp` is in the set.
        """
        if not 0 <= cp <= 0x10FFFF:
            return False
        char = chr(cp)
        idx = bisect_left(self._table, char)
        if idx >= len(self._table):
            return False
        return (idx % 2) == 1 or self._table[idx] == char

    def __eq__(self, rhs):
        return self._table == rhs._table

    def __repr__(self):
        elems = '\\n'.join(['%04X..%04X' % item for item in self.items()])
        return "CodepointSet('%s')" % elems

    def items(self):
        for i in range(len(self._table) // 2):
            lo = ord(self._table[2*i])
            hi = ord(self._table[2*i+1])
            yield (lo, hi)


_RANGE = re.compile(r'^\s*([0-9A-Fa-f]+)(?:\.\.([0-9A-Fa-f]+))?\s*$')


def _parse(table):
    elems = []
    for line in io.StringIO(table):
        m = _RANGE.match(line.strip())
        if not m:
            continue
        lo = int(m.group(1), 16)
        hi = int(m.group(2), 16) if m.group(2) else lo
        if lo > hi:
            raise ValueError('Range lo > hi')
        elems.append((lo, hi))
    return elems


def _coalesce(elems):
    elems.sort()
    i = 0
    while i < len(elems) - 1:
        (lo0, hi0), (lo1, hi1) = elems[i:i+2]
        if not lo0 <= hi0 < lo1 <= hi1:
            raise ValueError('Range overlaps at index %d: %r' % (i, elems[i:i+2]))
        if lo1 == hi0 + 1:
            elems[i:i+2] = [(lo0, hi1)]
        else:
            i += 1
    return elems
