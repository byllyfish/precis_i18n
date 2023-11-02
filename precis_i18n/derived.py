"""Implements the PRECIS (RFC 8264) `derived_property` function."""

PVALID = "PVALID"
FREE_PVAL = "FREE_PVAL"
DISALLOWED = "DISALLOWED"
UNASSIGNED = "UNASSIGNED"
CONTEXTJ = "CONTEXTJ"
CONTEXTO = "CONTEXTO"

# pylint: disable=too-many-return-statements,too-many-branches


def derived_property(cp, ucd):  # noqa: C901
    """Return value of the PRECIS derived property of a code point.

    From section 8 of RFC 8264:

       If .cp. .in. Exceptions Then Exceptions(cp);
       Else If .cp. .in. BackwardCompatible Then BackwardCompatible(cp);
       Else If .cp. .in. Unassigned Then UNASSIGNED;
       Else If .cp. .in. ASCII7 Then PVALID;
       Else If .cp. .in. JoinControl Then CONTEXTJ;
       Else If .cp. .in. OldHangulJamo Then DISALLOWED;
       Else If .cp. .in. PrecisIgnorableProperties Then DISALLOWED;
       Else If .cp. .in. Controls Then DISALLOWED;
       Else If .cp. .in. HasCompat Then ID_DIS or FREE_PVAL;
       Else If .cp. .in. LetterDigits Then PVALID;
       Else If .cp. .in. OtherLetterDigits Then ID_DIS or FREE_PVAL;
       Else If .cp. .in. Spaces Then ID_DIS or FREE_PVAL;
       Else If .cp. .in. Symbols Then ID_DIS or FREE_PVAL;
       Else If .cp. .in. Punctuation Then ID_DIS or FREE_PVAL;
       Else DISALLOWED;

    Args:
        cp (int): Code point.
        ucd (UnicodeData): Unicode character database.

    Returns:
        str: Derived property for `cp`.
    """
    category = ucd.category(chr(cp))

    if in_exceptions(cp):
        return exceptions(cp), "exceptions"
    if in_backward_compatible(cp):
        return backward_compatible(cp), "backward_compatible"  # pragma: no cover
    if in_unassigned(cp, category, ucd):
        return UNASSIGNED, "unassigned"
    if in_ascii7(cp):
        return PVALID, "ascii7"
    if in_join_control(cp):
        return CONTEXTJ, "join_control"
    if in_old_hangul_jamo(cp, ucd):
        return DISALLOWED, "old_hangul_jamo"
    if in_precis_ignorable_properties(cp, ucd):
        return DISALLOWED, "precis_ignorable_properties"
    if in_controls(cp, ucd):
        return DISALLOWED, "controls"
    if in_has_compat(cp, ucd):
        return FREE_PVAL, "has_compat"
    if in_letter_digits(category):
        return PVALID, "letter_digits"
    if in_other_letter_digits(category):
        return FREE_PVAL, "other_letter_digits"
    if in_spaces(category):
        return FREE_PVAL, "spaces"
    if in_symbols(category):
        return FREE_PVAL, "symbols"
    if in_punctuation(category):
        return FREE_PVAL, "punctuation"
    return DISALLOWED, "other"


def in_letter_digits(category):
    """Category for code points informally described as "language characters".

    Args:
        category (str): Unicode general category.

    Returns:
        bool: True if `category` in set.
    """
    return category in {"Ll", "Lu", "Lo", "Nd", "Lm", "Mn", "Mc"}


def in_exceptions(cp):
    """Code points for which the derived property cannot be assigned using
    only the Unicode core property values.

    Args:
        cp (int): Code point.

    Returns:
        bool: True if `cp` is in set.
    """
    return cp in _EXCEPTIONS_TABLE


def in_backward_compatible(cp):
    """Code points whose Unicode property values have changed such that their
    derived property changed.

    Args:
        cp (int): Code point.

    Returns:
        bool: True if `cp` is in set.
    """
    return cp in _BACKWARD_COMPATIBLE_TABLE


def in_join_control(cp):
    """Code points for Join Control characters required under some
    circumstances. (CONTEXTJ)

    Args:
        cp (int): Code point.

    Returns:
        bool: True if `cp` is in set.
    """
    return 0x200C <= cp <= 0x200D


def in_old_hangul_jamo(cp, ucd):
    """Code points for all conjoining Hangul Jamo (Leading Jamo, Vowel Jamo,
    and Trailing Jamo).

    Args:
        cp (int): Code point.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if `cp` is in set.
    """
    return ucd.old_hangul_jamo(cp)


def in_unassigned(cp, category, ucd):
    """Code points that are not (yet) assigned in Unicode.

    Args:
        cp (int): Code point.
        category (str): Unicode general category for `cp`.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if `cp` is in set.
    """
    return category == "Cn" and not ucd.noncharacter(cp)


def in_ascii7(cp):
    """Code points for all printable, non-space characters from the 7-bit
    ASCII range.

    Args:
        cp (int): Code point.

    Returns:
        bool: True if `cp` is in set.
    """
    return 0x21 <= cp <= 0x7E


def in_controls(cp, ucd):
    """Code points for all control characters.

    Args:
        cp (int): Code point.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if `cp` is in set.
    """
    return ucd.control(cp)


def in_precis_ignorable_properties(cp, ucd):
    """Code points that are discouraged from use in PRECIS string classes.

    Args:
        cp (int): Code point.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if `cp` is in set.
    """
    return ucd.default_ignorable(cp) or ucd.noncharacter(cp)


def in_spaces(category):
    """Category for code points that are space characters.

    Args:
        category (str): Unicode general category.

    Returns:
        bool: True if `category` in set.
    """
    return category in {"Zs"}


def in_symbols(category):
    """Category for code points that are symbols.

    Args:
        category (str): Unicode general category.

    Returns:
        bool: True if `category` in set.
    """
    return category in {"Sm", "Sc", "Sk", "So"}


def in_punctuation(category):
    """Category for code points that are punctuation characters.

    Args:
        category (str): Unicode general category.

    Returns:
        bool: True if `category` in set.
    """
    return category in {"Pc", "Pd", "Ps", "Pe", "Pi", "Pf", "Po"}


def in_has_compat(cp, ucd):
    """Code points that have compatibility equivalents.

    Args:
        cp (int): Code point.
        ucd (UnicodeData): Unicode character database.

    Returns:
        bool: True if `cp` is in set.
    """
    return ucd.has_compat(cp)


def in_other_letter_digits(category):
    """Code points that are letters and digits other than the "traditional"
    letters and digits.

    Args:
        category (str): Unicode general category.

    Returns:
        bool: True if `category` in set.
    """
    return category in {"Lt", "Nl", "No", "Me"}


def exceptions(cp):
    """Return derived property for exception codepoint.

    Args:
        cp (int): Code point.

    Returns:
        str: Derived property for `cp`.
    """
    return _EXCEPTIONS_TABLE[cp]


def backward_compatible(cp):  # pragma: no cover
    """Return derived property for backward-compatible code point.

    Args:
        cp (int): Code point.

    Returns:
        str: Derived property for `cp`.
    """
    return _BACKWARD_COMPATIBLE_TABLE[cp]


_EXCEPTIONS_TABLE = {
    # Source: RFC 5892, Section 2.6, pp. 7-8.
    # PVALID -- Would otherwise have been DISALLOWED
    0x00DF: PVALID,  # LATIN SMALL LETTER SHARP S
    0x03C2: PVALID,  # GREEK SMALL LETTER FINAL SIGMA
    0x06FD: PVALID,  # ARABIC SIGN SINDHI AMPERSAND
    0x06FE: PVALID,  # ARABIC SIGN SINDHI POSTPOSITION MEN
    0x0F0B: PVALID,  # TIBETAN MARK INTERSYLLABIC TSHEG
    0x3007: PVALID,  # IDEOGRAPHIC NUMBER ZERO
    # CONTEXTO -- Would otherwise have been DISALLOWED
    0x00B7: CONTEXTO,  # MIDDLE DOT
    0x0375: CONTEXTO,  # GREEK LOWER NUMERAL SIGN (KERAIA)
    0x05F3: CONTEXTO,  # HEBREW PUNCTUATION GERESH
    0x05F4: CONTEXTO,  # HEBREW PUNCTUATION GERSHAYIM
    0x30FB: CONTEXTO,  # KATAKANA MIDDLE DOT
    # CONTEXTO -- Would otherwise have been PVALID
    0x0660: CONTEXTO,  # ARABIC-INDIC DIGIT ZERO
    0x0661: CONTEXTO,  # ARABIC-INDIC DIGIT ONE
    0x0662: CONTEXTO,  # ARABIC-INDIC DIGIT TWO
    0x0663: CONTEXTO,  # ARABIC-INDIC DIGIT THREE
    0x0664: CONTEXTO,  # ARABIC-INDIC DIGIT FOUR
    0x0665: CONTEXTO,  # ARABIC-INDIC DIGIT FIVE
    0x0666: CONTEXTO,  # ARABIC-INDIC DIGIT SIX
    0x0667: CONTEXTO,  # ARABIC-INDIC DIGIT SEVEN
    0x0668: CONTEXTO,  # ARABIC-INDIC DIGIT EIGHT
    0x0669: CONTEXTO,  # ARABIC-INDIC DIGIT NINE
    0x06F0: CONTEXTO,  # EXTENDED ARABIC-INDIC DIGIT ZERO
    0x06F1: CONTEXTO,  # EXTENDED ARABIC-INDIC DIGIT ONE
    0x06F2: CONTEXTO,  # EXTENDED ARABIC-INDIC DIGIT TWO
    0x06F3: CONTEXTO,  # EXTENDED ARABIC-INDIC DIGIT THREE
    0x06F4: CONTEXTO,  # EXTENDED ARABIC-INDIC DIGIT FOUR
    0x06F5: CONTEXTO,  # EXTENDED ARABIC-INDIC DIGIT FIVE
    0x06F6: CONTEXTO,  # EXTENDED ARABIC-INDIC DIGIT SIX
    0x06F7: CONTEXTO,  # EXTENDED ARABIC-INDIC DIGIT SEVEN
    0x06F8: CONTEXTO,  # EXTENDED ARABIC-INDIC DIGIT EIGHT
    0x06F9: CONTEXTO,  # EXTENDED ARABIC-INDIC DIGIT NINE
    # DISALLOWED -- Would otherwise have been PVALID
    0x0640: DISALLOWED,  # ARABIC TATWEEL
    0x07FA: DISALLOWED,  # NKO LAJANYALAN
    0x302E: DISALLOWED,  # HANGUL SINGLE DOT TONE MARK
    0x302F: DISALLOWED,  # HANGUL DOUBLE DOT TONE MARK
    0x3031: DISALLOWED,  # VERTICAL KANA REPEAT MARK
    0x3032: DISALLOWED,  # VERTICAL KANA REPEAT WITH VOICED SOUND MARK
    0x3033: DISALLOWED,  # VERTICAL KANA REPEAT MARK UPPER HALF
    0x3034: DISALLOWED,  # VERTICAL KANA REPEAT WITH VOICED SOUND MARK UPPER HA
    0x3035: DISALLOWED,  # VERTICAL KANA REPEAT MARK LOWER HALF
    0x303B: DISALLOWED,  # VERTICAL IDEOGRAPHIC ITERATION MARK
}

_BACKWARD_COMPATIBLE_TABLE = {}
