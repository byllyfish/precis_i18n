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

    This class is constructed from a multi-line string containing a sequence of
    codepoints and codepoint ranges.

      HHHH
      HHHH..HHHH

    H is a hexadecimal digit.

    Note: Sets with any non-BMP codepoints will use 32-bits for all codepoints. 
    (PEP 393 Flexible String Representation)
    """

    def __init__(self, table):
        """ Construct set from a string containing codepoint ranges.
        """
        self._table = _stringify(_coalesce(_parse(table)))
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
        """ Return true if two sets are equal.
        """
        return self._table == rhs._table

    def __repr__(self):
        """ Return string representation of set.
        """
        elems = '\\n'.join(_repr(elem) for elem in self.items())
        return "CodepointSet('%s')" % elems

    def items(self):
        """ Generator yielding sequence of range tuples (lo, hi).
        """
        for i in range(len(self._table) // 2):
            lo = ord(self._table[2*i])
            hi = ord(self._table[2*i+1])
            yield (lo, hi)


def _parse(table):
    """ Parse a multi-line string containing a codepoint or codepoint range.

    Return a list of tuples (lo, hi).
    """
    codepoint = re.compile(r'^([0-9A-Fa-f]+)(?:\.\.([0-9A-Fa-f]+))?$')
    elems = []
    for line in io.StringIO(table):
        line = line.strip()
        m = codepoint.match(line)
        if not m:
            if line and line[0] != '#':
                raise ValueError('Unable to parse line: %s' % line)
            continue
        lo = int(m.group(1), 16)
        hi = int(m.group(2), 16) if m.group(2) else lo
        if lo > hi:
            raise ValueError('Range lo > hi')
        elems.append((lo, hi))
    return elems


def _coalesce(elems):
    """ Sort elements and coalesce adjacent ranges.
    """
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


def _stringify(elems):
    """ Convert a sequence of ranges into a unicode string.
    """
    return ''.join(chr(lo) + chr(hi) for (lo, hi) in elems)


def _repr(elem):
    """ Return string representation for tuple (lo, hi)
    """
    if elem[0] == elem[1]:
        return '%04X' % elem[0]
    else:
        return '%04X..%04X' % elem
