"""
Implements the BiDi Rule from RFC 5893, Section 2.
"""

# The Bidi Rule (Source: RFC 5893, Section 2)
#
# The following rule, consisting of six conditions, applies to labels
# in Bidi domain names.  The requirements that this rule satisfies are
# described in Section 3.  All of the conditions must be satisfied for
# the rule to be satisfied.
#
# 1.  The first character must be a character with Bidi property L, R,
#    or AL.  If it has the R or AL property, it is an RTL label; if it
#    has the L property, it is an LTR label.
#
# 2.  In an RTL label, only characters with the Bidi properties R, AL,
#    AN, EN, ES, CS, ET, ON, BN, or NSM are allowed.
#
# 3.  In an RTL label, the end of the label must be a character with
#    Bidi property R, AL, EN, or AN, followed by zero or more
#    characters with Bidi property NSM.
#
# 4.  In an RTL label, if an EN is present, no AN may be present, and
#    vice versa.
#
# 5.  In an LTR label, only characters with the Bidi properties L, EN,
#    ES, CS, ET, ON, BN, or NSM are allowed.
#
# 6.  In an LTR label, the end of the label must be a character with
#    Bidi property L or EN, followed by zero or more characters with
#    Bidi property NSM.

_LTR_FIRST = {'L'}
_LTR_ALLOWED = {'L', 'EN', 'ES', 'CS', 'ET', 'ON', 'BN', 'NSM'}
_LTR_LAST = {'L', 'EN'}
_LTR_EXCL = {}

_RTL_FIRST = {'R', 'AL'}
_RTL_ALLOWED = {'R', 'AL', 'AN', 'EN', 'ES', 'CS', 'ET', 'ON', 'BN', 'NSM'}
_RTL_LAST = {'R', 'AL', 'EN', 'AN'}
_RTL_EXCL = {'EN', 'AN'}

_RTL_ANY = {'R', 'AL', 'AN'}


def bidi_rule(value, ucd):
    """ Return true if `value` obeys the "BiDi" rule.
    """
    bidi = ucd.bidirectional(value[0])
    if bidi in _LTR_FIRST:
        return _bidi_rule(value, ucd, _LTR_ALLOWED, _LTR_LAST, _LTR_EXCL)
    elif bidi in _RTL_FIRST:
        return _bidi_rule(value, ucd, _RTL_ALLOWED, _RTL_LAST, _RTL_EXCL)
    else:
        return False


def _bidi_rule(value, ucd, allowed, last, exclusive):
    """ Checks the bidi_rule for LTR or RTL, depending on parameters.
    """
    assert ucd.bidirectional(value[0]) in (_LTR_FIRST | _RTL_FIRST)
    # Starting from the end, find the first character whose bidi is not 'NSM'.
    found = -1
    for i in reversed(range(len(value))):
        bidi = ucd.bidirectional(value[i])
        if bidi != 'NSM':
            found = i
            break
    # Last non-NSM character must be in `last`.
    if found < 0 or bidi not in last:
        return False
    # Check if last char is in the exclusive set.
    bidi_seen = bidi if bidi in exclusive else None
    # Make sure the remaining characters are allowed.
    for i in range(1, found):
        bidi = ucd.bidirectional(value[i])
        if bidi not in allowed:
            return False
        if bidi in exclusive and bidi_seen != bidi:
            if bidi_seen:
                return False
            bidi_seen = bidi
    return True


def has_rtl(value, ucd):
    """ Return true if string value contains any RTL characters.
    """
    return any(ucd.bidirectional(x) in _RTL_ANY for x in value)
