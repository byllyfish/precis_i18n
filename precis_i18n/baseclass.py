"""Implements the PRECIS string classes."""

from functools import lru_cache

from precis_i18n.context import _context_rule_error
from precis_i18n.derived import CONTEXTJ, CONTEXTO, FREE_PVAL, PVALID, derived_property
from precis_i18n.unicode import UnicodeData


_CLASSIFICATION_OVERRIDES = frozenset((
    "category", "control", "default_ignorable", "has_compat", "noncharacter",
    "normalize", "old_hangul_jamo",
))


@lru_cache(maxsize=1)
def _native_common_properties():
    """Classify Basic Latin through Combining Diacritical Marks once."""
    native = UnicodeData()
    # A fixed table of public Unicode data, independent of input values.
    return tuple(derived_property(cp, native) for cp in range(0x0370))


class BaseClass:
    """Abstract base class for all String classes in PRECIS framework.

    Subclasses must set `_allowed` to a tuple of derived property names. For
    example, `_allowed = (PVALID, )`.

    Args:
        ucd (UnicodeData): Unicode character database.
        name (str): String class name.

    Attributes:
        ucd (UnicodeData): Unicode character database.
        name (str): String class name.
    """

    _allowed = ()

    def __init__(self, ucd, name=None):
        self.ucd = ucd
        self.name = name or self.__class__.__name__

    def enforce(self, value, codec_name=None):
        """Ensure that all characters in `value` are allowed by the string class.

        Args:
            value (str): String value to enforce.
            codec_name (Optional[str]): Codec name to report in exceptions. If
                None, use `self.name`.

        Returns:
            str: Enforced value.

        Raises:
            UnicodeEncodeError: Value is disallowed by the string class.
        """
        if codec_name is None:
            codec_name = self.name

        ucd = self.ucd
        allowed = self._allowed
        properties = ()
        if (type(value) is str and type(ucd) is UnicodeData and ucd.mode == "native"
                and _CLASSIFICATION_OVERRIDES.isdisjoint(vars(ucd))):
            # All printable ASCII except space is PVALID. Space is FREE_PVAL.
            # A failed shortcut falls through to preserve the exact error.
            if value.isascii() and value.isprintable() and PVALID in allowed:
                if FREE_PVAL in allowed or " " not in value:
                    return value
            properties = _native_common_properties()

        limit = len(properties)
        whole_string_results = None
        for i, char in enumerate(value):
            cp = ord(char)
            prop, kind = properties[cp] if cp < limit else derived_property(cp, ucd)
            if prop in allowed:
                continue

            if prop in (CONTEXTJ, CONTEXTO):
                # Check each occurrence. Reuse verdicts only for rules that
                # depend on the whole string and are invariant at each offset.
                if whole_string_results is None:
                    whole_string_results = {}
                kind = _context_rule_error(value, i, ucd, whole_string_results)
                if not kind:
                    continue

            raise_error(codec_name, value, i, kind)

        return value

    def comparison_key(self, value):
        """Return the exact bytes of an admitted value without profile mapping."""
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return self.enforce(value).encode("utf-8")


class IdentifierClass(BaseClass):
    """Concrete class representing PRECIS IdentifierClass from RFC 8264.

    Args:
        ucd (UnicodeData): Unicode character database.
        name (str): String class name.
    """

    _allowed = (PVALID,)


class FreeFormClass(BaseClass):
    """Concrete class repsenting PRECIS FreeFormClass from RFC 8264.

    Args:
        ucd (UnicodeData): Unicode character database.
        name (str): String class name.
    """

    _allowed = (PVALID, FREE_PVAL)


def raise_error(encoding, value, offset, error):
    """Raise specially formatted UnicodeEncodeError exception.

    Args:
        encoding (str): Name of the encoding/codec.
        value (str): Value being encoded.
        offset (int): Offset in `value` where error detected. Use -1 to
            indicate the entire string.
        error (str): Subtype of error detected.

    Raises:
        UnicodeEncodeError: Always.
    """
    if offset < 0:
        start = 0
        end = len(value)
    else:
        start = offset
        end = offset + 1

    reason = "DISALLOWED/%s" % error
    raise UnicodeEncodeError(encoding, value, start, end, reason)
