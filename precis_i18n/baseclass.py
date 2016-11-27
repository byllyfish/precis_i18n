"""
Implements the PRECIS string classes.
"""

from precis_i18n.context import context_rule_error
from precis_i18n.derived import (CONTEXTJ, CONTEXTO, FREE_PVAL, PVALID,
                                 derived_property)


class BaseClass(object):
    """ Abstract base class for all String classes in PRECIS framework.

    Subclasses must set `_allowed` to a tuple of derived property names.
    """
    _allowed = ()

    def __init__(self, ucd, name):
        self._ucd = ucd
        self._name = name

    @property
    def ucd(self):
        """ Unicode character database.
        """
        return self._ucd

    @property
    def name(self):
        """ The profile's name.
        """
        return self._name

    def enforce(self, value, codec_name=None):
        """ Ensure that all characters in `value` are allowed by the string
        class.

        Return UTF-8 `value` or raise a `UnicodeEncodeError`.
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
    """ Concrete class representing PRECIS IdentifierClass from RFC 7564.
    """
    _allowed = (PVALID, )

    def __init__(self, ucd, name='IdentifierClass'):
        super().__init__(ucd, name)


class FreeFormClass(BaseClass):
    """ Concrete class repsenting PRECIS FreeFormClass from RFC 7564.
    """
    _allowed = (PVALID, FREE_PVAL)

    def __init__(self, ucd, name='FreeFormClass'):
        super().__init__(ucd, name)


def raise_error(encoding, value, offset, error):
    """ Raise formatted UnicodeEncodeError exception.
    """
    if offset < 0:
        start = 0
        end = len(value)
    else:
        start = offset
        end = offset + 1

    reason = 'DISALLOWED/%s' % error
    raise UnicodeEncodeError(encoding, value, start, end, reason)
