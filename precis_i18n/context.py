"""
Implements PRECIS context rules for characters with derived properties of
CONTEXTJ and CONTEXTO.
"""


def context_rule_error(value, offset, ucd):
    """ Apply the context rule to `value[offset]`.

    Return '' if there is no error. Return name of the rule if it fails.
    """
    cp = ord(value[offset])
    if ucd.arabic_indic(cp):
        rule = rule_arabic_indic
    elif ucd.extended_arabic_indic(cp):
        rule = rule_extended_arabic_indic
    else:
        rule = _RULES[cp]

    try:
        valid = rule(value, offset, ucd)
    except IndexError:
        # Handle failure of _before and _after accessors.
        valid = False

    if valid:
        return ''

    # If context rule fails, return name of context rule (the name of the
    # function with 'rule_' prefix removed.)
    result = rule.__name__
    if result.startswith('rule_'):
        result = result[5:]
    return result


def context_rule(value, offset, ucd):
    """ Apply the context rule to `value[offset]`.

    Return true if successful.
    """
    return not context_rule_error(value, offset, ucd)


# These rules test a character at a given offset in the string.


def rule_zero_width_nonjoiner(value, offset, ucd):
    """ Return true if context permits a ZERO WIDTH NON-JOINER (U+200C).

    From https://tools.ietf.org/html/rfc5892#appendix-A.1:

      "This may occur in a formally cursive script (such as Arabic) in a
      context where it breaks a cursive connection as required for
      orthographic rules, as in the Persian language, for example.  It
      also may occur in Indic scripts in a consonant-conjunct context
      (immediately following a virama), to control required display of
      such conjuncts."
    """
    assert value[offset] == '\u200c'
    if ucd.combining_virama(_before(value, offset)):
        return True
    if ucd.valid_jointype(value, offset):
        return True
    return False


def rule_zero_width_joiner(value, offset, ucd):
    """ Return true if context permits a ZERO WIDTH JOINER (U+200D).

    From https://tools.ietf.org/html/rfc5892#appendix-A.2:

      "This may occur in Indic scripts in a consonant-conjunct context
      (immediately following a virama), to control required display of
      such conjuncts."
    """
    assert value[offset] == '\u200d'
    return ucd.combining_virama(_before(value, offset))


def rule_middle_dot(value, offset, ucd):
    """ Return true if context permits a MIDDLE DOT (U+00B7).

    From https://tools.ietf.org/html/rfc5892#appendix-A.3:

      "Between 'l' (U+006C) characters only, used to permit the Catalan
      character ela geminada to be expressed."
    """
    # pylint: disable=unused-argument
    assert value[offset] == '\u00b7'
    return 0x06c == _before(value, offset) == _after(value, offset)


def rule_greek(value, offset, ucd):
    """ Return true if context permits GREEK LOWER NUMERAL SIGN (U+0375).

    From https://tools.ietf.org/html/rfc5892#appendix-A.4:

      "The script of the following character MUST be Greek."
    """
    assert value[offset] == '\u0375'
    return ucd.greek_script(_after(value, offset))


def rule_hebrew(value, offset, ucd):
    """ Return true if context permits HEBREW PUNCTUATION GERESH or GERSHAYIM
    (U+05F3, U+05F4).

    From https://tools.ietf.org/html/rfc5892#appendix-A.5,
         https://tools.ietf.org/html/rfc5892#appendix-A.6:

      "The script of the preceding character MUST be Hebrew."
    """
    assert value[offset] in '\u05f3\u05f4'
    return ucd.hebrew_script(_before(value, offset))


# These rules ignore the offset argument; they test the entire string. A string
# only needs to be tested once, irrespective of the number of times the rule is
# triggered.


def rule_katakana_middle_dot(value, offset, ucd):
    """ Return true if context permits KATAKANA MIDDLE DOT (U+30FB).

    From https://tools.ietf.org/html/rfc5892#appendix-A.7:

      "Note that the Script of Katakana Middle Dot is not any of
      "Hiragana", "Katakana", or "Han".  The effect of this rule is to
      require at least one character in the label to be in one of those
      scripts."
    """
    assert value[offset] == '\u30fb'
    return any(ucd.hiragana_katakana_han_script(ord(x)) for x in value)


def rule_arabic_indic(value, offset, ucd):
    """ Return true if context permits ARABIC-INDIC DIGITS (U+0660..U+0669).

    From https://tools.ietf.org/html/rfc5892#appendix-A.8:

      "Can not be mixed with Extended Arabic-Indic Digits."
    """
    assert ucd.arabic_indic(ord(value[offset]))
    return not any(ucd.extended_arabic_indic(ord(x)) for x in value)


def rule_extended_arabic_indic(value, offset, ucd):
    """ Return true if context permits EXTENDED ARABIC-INDIC DIGITS
    (U+06F0..U+06F9).

    From https://tools.ietf.org/html/rfc5892#appendix-A.9:

      "Can not be mixed with Arabic-Indic Digits."
    """
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
