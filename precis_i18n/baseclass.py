"""Implements the PRECIS string classes."""

from precis_i18n.context import context_rule_error
from precis_i18n.derived import (CONTEXTJ, CONTEXTO, FREE_PVAL, PVALID,
                                 derived_property)


class BaseClass(object):
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

    def __init__(self, ucd, name):
        self.ucd = ucd
        self.name = name

    def enforce(self, value, codec_name=None):
        """Ensure that all characters in `value` are allowed by the string class.

        Args:
            value (str): String value to enforce.
            codec_name (Optional[str]): Codec name to report in exceptions. If
                None, use `self.name`.

        Returns:
            bytes: Value encoded in UTF-8.

        Raises:
            UnicodeEncodeError: Value is disallowed by the string class.
        """
        if codec_name is None:
            codec_name = self.name

        for i, char in enumerate(value):
            prop, kind = derived_property(ord(char), self.ucd)
            if prop in self._allowed:
                continue

            if prop == CONTEXTJ or prop == CONTEXTO:
                # Replace `kind` ('exceptions', 'join_control') with the
                # specific name of the context rule, if the rule fails.
                kind = context_rule_error(value, i, self.ucd)
                if not kind:
                    continue

            raise_error(codec_name, value, i, kind)

        return value.encode('utf-8')


class IdentifierClass(BaseClass):
    """Concrete class representing PRECIS IdentifierClass from RFC 7564.

    Args:
        ucd (UnicodeData): Unicode character database.
        name (str): String class name.
    """
    _allowed = (PVALID, )

    def __init__(self, ucd, name='IdentifierClass'):
        super().__init__(ucd, name)


class FreeFormClass(BaseClass):
    """Concrete class repsenting PRECIS FreeFormClass from RFC 7564.

    Args:
        ucd (UnicodeData): Unicode character database.
        name (str): String class name.
    """
    _allowed = (PVALID, FREE_PVAL)

    def __init__(self, ucd, name='FreeFormClass'):
        super().__init__(ucd, name)


def raise_error(encoding, value, offset, error):
    """Raise specially formatted UnicodeEncodeError exception.

    Args:
        encoding (str): Name of the encoding/codec.
        value (str): Value being encoded.
        offset (int): Offset in `value` where error detected. Use -1 to indicate
            the entire string.
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

    reason = 'DISALLOWED/%s' % error
    raise UnicodeEncodeError(encoding, value, start, end, reason)
