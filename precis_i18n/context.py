""" 
Implements PRECIS context rules for characters with derived properties of
CONTEXTJ and CONTEXTO.
"""

def context_rule(value, offset, ucd):
    """ Apply the context rule to `value[offset]`.

    Return true if successful.
    """
    cp = ord(value[offset])
    try:
        if ucd.arabic_indic(cp):
            return rule_arabic_indic(value, offset, ucd)
        elif ucd.extended_arabic_indic(cp):
            return rule_extended_arabic_indic(value, offset, ucd)
        else:
            return _RULES[cp](value, offset, ucd)
    except IndexError:
        # Handle failure of _before and _after accessors.
        return False


# These rules test a character at a given offset in the string.

def rule_zero_width_nonjoiner(value, offset, ucd):
    assert value[offset] == '\u200c'
    if ucd.combining_virana(_before(value, offset)):
        return True
    if ucd.valid_jointype(value, offset):
        return True
    return False


def rule_zero_width_joiner(value, offset, ucd):
    assert value[offset] == '\u200d'
    return ucd.combining_virana(_before(value, offset))


def rule_middle_dot(value, offset, ucd):
    assert value[offset] == '\u00b7'
    return _before(value, offset) == 0x06c and _after(value, offset) == 0x06c


def rule_greek(value, offset, ucd):
    assert value[offset] == '\u0375'
    return ucd.greek_script(_after(value, offset))


def rule_hebrew(value, offset, ucd):
    assert value[offset] in '\u05f3\u05f4'
    return ucd.hebrew_script(_before(value, offset))

# These rules ignore the offset argument; they test the entire string. A string
# only needs to be tested once, irrespective of the number of times the rule is
# triggered.


def rule_katakana_middle_dot(value, offset, ucd):
    assert value[offset] == '\u30fb'
    return any(ucd.hiragana_katakana_han_script(ord(x)) for x in value)


def rule_arabic_indic(value, offset, ucd):
    assert ucd.arabic_indic(ord(value[offset]))
    return not any(ucd.extended_arabic_indic(ord(x)) for x in value)


def rule_extended_arabic_indic(value, offset, ucd):
    assert ucd.extended_arabic_indic(ord(value[offset]))
    return not any(ucd.arabic_indic(ord(x)) for x in value)


_RULES = {
    0x200c: rule_zero_width_nonjoiner,
    0x200d: rule_zero_width_joiner,
    0x00b7: rule_middle_dot,
    0x0375: rule_greek,
    0x05f3: rule_hebrew,
    0x05f4: rule_hebrew,
    0x30fb: rule_katakana_middle_dot,
}


def _before(value, offset):
    if offset <= 0:
        raise IndexError(offset - 1)
    return ord(value[offset - 1])


def _after(value, offset):
    return ord(value[offset + 1])
