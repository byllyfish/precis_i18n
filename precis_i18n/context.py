"""Implements PRECIS rules for derived properties CONTEXTJ and CONTEXTO."""


def context_rule_error(value, offset, ucd):
    """Apply the PRECIS context rules to `value[offset]`.

    Args:
        value (str): String value to check.
        offset (int): Position within `value`.
        ucd (UnicodeData): Unicode character database.

    Returns:
        str: '' if no error, or name of the rule that failed.
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
        return ""

    # If context rule fails, return name of context rule (the name of the
    # function with 'rule_' prefix removed.)
    result = rule.__name__
    if result.startswith("rule_"):
        result = result[5:]
    return result


# These rules test a character at a given offset in the string.


def rule_zero_width_nonjoiner(value, offset, ucd):
    """Return true if context permits a ZERO WIDTH NON-JOINER (U+200C).

    From https://tools.ietf.org/html/rfc5892#appendix-A.1:

      "This may occur in a formally cursive script (such as Arabic) in a
      context where it breaks a cursive connection as required for
      orthographic rules, as in the Persian language, for example.  It
      also may occur in Indic scripts in a consonant-conjunct context
      (immediately following a virama), to control required display of
      such conjuncts."

    Args:
        value (str): String value to check.
        offset (int): Position within `value`.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if value is allowed.
    """
    assert value[offset] == "\u200c"
    if ucd.combining_virama(_before(value, offset)):
        return True
    if ucd.valid_jointype(value, offset):
        return True
    return False


def rule_zero_width_joiner(value, offset, ucd):
    """Return true if context permits a ZERO WIDTH JOINER (U+200D).

    From https://tools.ietf.org/html/rfc5892#appendix-A.2:

      "This may occur in Indic scripts in a consonant-conjunct context
      (immediately following a virama), to control required display of
      such conjuncts."

    Args:
        value (str): String value to check.
        offset (int): Position within `value`.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if value is allowed.
    """
    assert value[offset] == "\u200d"
    return ucd.combining_virama(_before(value, offset))


def rule_middle_dot(value, offset, ucd):
    """Return true if context permits a MIDDLE DOT (U+00B7).

    From https://tools.ietf.org/html/rfc5892#appendix-A.3:

      "Between 'l' (U+006C) characters only, used to permit the Catalan
      character ela geminada to be expressed."

    Args:
        value (str): String value to check.
        offset (int): Position within `value`.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if value is allowed.
    """
    # pylint: disable=unused-argument
    assert value[offset] == "\u00b7"
    return 0x06C == _before(value, offset) == _after(value, offset)


def rule_greek_keraia(value, offset, ucd):
    """Return true if context permits GREEK LOWER NUMERAL SIGN (U+0375).

    From https://tools.ietf.org/html/rfc5892#appendix-A.4:

      "The script of the following character MUST be Greek."

    Args:
        value (str): String value to check.
        offset (int): Position within `value`.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if value is allowed.
    """
    assert value[offset] == "\u0375"
    return ucd.greek_script(_after(value, offset))


def rule_hebrew_punctuation(value, offset, ucd):
    """Return true if context permits HEBREW PUNCTUATION GERESH or GERSHAYIM
    (U+05F3, U+05F4).

    From https://tools.ietf.org/html/rfc5892#appendix-A.5,
         https://tools.ietf.org/html/rfc5892#appendix-A.6:

      "The script of the preceding character MUST be Hebrew."

    Args:
        value (str): String value to check.
        offset (int): Position within `value`.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if value is allowed.
    """
    assert value[offset] in "\u05f3\u05f4"
    return ucd.hebrew_script(_before(value, offset))


# These rules ignore the offset argument; they test the entire string. A string
# only needs to be tested once, irrespective of the number of times the rule is
# triggered.


def rule_katakana_middle_dot(value, offset, ucd):
    """Return true if context permits KATAKANA MIDDLE DOT (U+30FB).

    From https://tools.ietf.org/html/rfc5892#appendix-A.7:

      "Note that the Script of Katakana Middle Dot is not any of
      "Hiragana", "Katakana", or "Han".  The effect of this rule is to
      require at least one character in the label to be in one of those
      scripts."

    Args:
        value (str): String value to check.
        offset (int): Position within `value`.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if value is allowed.
    """
    assert value[offset] == "\u30fb"
    return any(ucd.hiragana_katakana_han_script(ord(x)) for x in value)


def rule_arabic_indic(value, offset, ucd):
    """Return true if context permits ARABIC-INDIC DIGITS (U+0660..U+0669).

    From https://tools.ietf.org/html/rfc5892#appendix-A.8:

      "Can not be mixed with Extended Arabic-Indic Digits."

    Args:
        value (str): String value to check.
        offset (int): Position within `value`.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if value is allowed.
    """
    assert ucd.arabic_indic(ord(value[offset]))
    return not any(ucd.extended_arabic_indic(ord(x)) for x in value)


def rule_extended_arabic_indic(value, offset, ucd):
    """Return true if context permits EXTENDED ARABIC-INDIC DIGITS
    (U+06F0..U+06F9).

    From https://tools.ietf.org/html/rfc5892#appendix-A.9:

      "Can not be mixed with Arabic-Indic Digits."

    Args:
        value (str): String value to check.
        offset (int): Position within `value`.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if value is allowed.
    """
    assert ucd.extended_arabic_indic(ord(value[offset]))
    return not any(ucd.arabic_indic(ord(x)) for x in value)


_RULES = {
    0x200C: rule_zero_width_nonjoiner,
    0x200D: rule_zero_width_joiner,
    0x00B7: rule_middle_dot,
    0x0375: rule_greek_keraia,
    0x05F3: rule_hebrew_punctuation,
    0x05F4: rule_hebrew_punctuation,
    0x30FB: rule_katakana_middle_dot,
}


def _before(value, offset):
    """Return code point before `value[offset]` or raise IndexError."""
    if offset <= 0:
        raise IndexError(offset - 1)
    return ord(value[offset - 1])


def _after(value, offset):
    """Return code point after `value[offset]` or raise IndexError."""
    return ord(value[offset + 1])
