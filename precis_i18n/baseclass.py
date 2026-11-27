"""Implements the PRECIS string classes."""

from _thread import allocate_lock
from functools import lru_cache
import re
from typing import Mapping, NamedTuple

from precis_i18n.context import _context_rule_error
from precis_i18n.derived import (
    CONTEXTJ, CONTEXTO, FREE_PVAL, PVALID,
    _EXCEPTIONS_TABLE, _FREEFORM_CATEGORIES, _LETTER_DIGITS, derived_property,
)
from precis_i18n.unicode import UnicodeData


_CLASSIFICATION_OVERRIDES = frozenset((
    "category", "control", "default_ignorable", "has_compat", "noncharacter",
    "normalize", "old_hangul_jamo",
))
_NATIVE_LOCK = allocate_lock()
_NATIVE_FLAGS = None
_CLASS_MASKS = {(PVALID,): 1, (PVALID, FREE_PVAL): 2}
_PROPERTY_FLAGS = {PVALID: 3, FREE_PVAL: 2}


class _NativeAdmission(NamedTuple):
    codes: bytes
    outcomes: tuple
    exception_pages: Mapping[int, int]


def _native_common_properties():
    """Store native admission bits for Basic Latin through Combining Marks."""
    global _NATIVE_FLAGS
    if _NATIVE_FLAGS is None:
        with _NATIVE_LOCK:
            if _NATIVE_FLAGS is None:
                _NATIVE_FLAGS = _build_native_admission()
    return _NATIVE_FLAGS


def _build_native_admission():
    native = UnicodeData()
    # The low two bits indicate admission. The other bits index the unchanged
    # classification and diagnostic only when a character needs more work.
    codes = {}
    packed = bytearray()
    for cp in range(0x0370):
        outcome = derived_property(cp, native)
        code = codes.get(outcome)
        if code is None:
            code = (len(codes) << 2) | _PROPERTY_FLAGS.get(outcome[0], 0)
            codes[outcome] = code
        packed.append(code)
    return _NativeAdmission(bytes(packed), tuple(codes), native._tables.exception_pages)


@lru_cache(maxsize=2)
def _bulk_pattern(mask):
    """Compile admitted ranges for long strings wholly in the packed domain."""
    ranges = []
    start = None
    for cp, flags in enumerate(_native_common_properties().codes + b"\0"):
        if flags & mask:
            if start is None:
                start = cp
        elif start is not None:
            ranges.append(r"\u{:04x}-\u{:04x}".format(start, cp - 1))
            start = None
    return re.compile("[" + "".join(ranges) + "]+")


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
        properties = b""
        outcomes = ()
        mask = 0
        if (type(value) is str and type(ucd) is UnicodeData and ucd._stock_admission
                and _CLASSIFICATION_OVERRIDES.isdisjoint(vars(ucd))):
            # All printable ASCII except space is PVALID. Space is FREE_PVAL.
            # A failed shortcut falls through to preserve the exact error.
            if value.isascii() and value.isprintable() and PVALID in allowed:
                if FREE_PVAL in allowed or " " not in value:
                    return value
            if isinstance(allowed, tuple):
                mask = _CLASS_MASKS.get(allowed, 0)
            if mask:
                if ucd.mode == "native":
                    properties, outcomes, exceptions = _native_common_properties()
                    if len(value) >= 128 and _bulk_pattern(mask).fullmatch(value):
                        return value
                else:
                    exceptions = ucd._tables.exception_pages

        limit = len(properties)
        whole_string_results = None
        for i, char in enumerate(value):
            cp = ord(char)
            if cp < limit:
                code = properties[cp]
                if code & mask:
                    continue
                prop, kind = outcomes[code >> 2]
            elif mask:
                prop = _EXCEPTIONS_TABLE.get(cp)
                if prop is not None:
                    kind = "exceptions"
                else:
                    page = exceptions.get(cp >> 8, 0)
                    if not page or not page & (1 << (cp & 255)):
                        category = ucd._ucd.category(char)
                        # Freeform admits both the ordinary categories and
                        # their compatibility variants. Identifier requires
                        # a letter/digit category and exact NFKC identity.
                        if mask == 2:
                            if category in _FREEFORM_CATEGORIES:
                                continue
                        elif category in _LETTER_DIGITS and ucd._ucd.normalize("NFKC", char) == char:
                            continue
                    prop, kind = derived_property(cp, ucd)
            else:
                prop, kind = derived_property(cp, ucd)
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
