import io
import re


class CodepointSet(object):
    """ Concrete class for a set of Unicode code points.

    Inclusive ranges [a, b] are stored as adjacent unicode characters in a
    string. The low end of a range has an even index. The high end is at an
    odd index. Singleton ranges are stored as [c, c].

    To test if a code point is in the set, search for the code point. If it
    matches a char in the string, the code point is in the set. If not, find
    the index of the next largest char. If this index is odd, the code point is
    in the set.
    """
    RANGE = re.compile(r'^\s*([0-9A-Fa-f]+)(?:\.\.([0-9A-Fa-f]+))?\s*$')

    def __init__(self, table):
        elems = self._parse(table)
        self._table = ''.join([chr(lo) + chr(hi) for (lo, hi) in elems])

    def __contains__(self, cp):
        assert isinstance(cp, int)
        # Binary search.
        lo, hi = 0, len(self._table)
        while lo < hi:
            mid = int((lo + hi) / 2)
            elem = ord(self._table[mid])
            if cp == elem:
                return True
            if cp < elem:
                hi = mid
            else:
                lo = mid + 1
        return (lo % 2) == 1

    def _parse(self, table):
        elems = []
        for line in io.StringIO(table):
            line = line.strip()
            if not line:
                continue
            m = self.RANGE.match(line)
            if not m:
                continue
            lo = int(m.group(1), 16)
            hi = int(m.group(2), 16) if m.group(2) else lo
            assert lo <= hi
            elems.append((lo, hi))
        elems.sort()
        # TODO: coalesce adjacent ranges after sorting.
        return elems
