"""
Implements the PRECIS string classes.
"""

from precis_i18n.context import context_rule
from precis_i18n.derived import (CONTEXTJ, CONTEXTO, FREE_PVAL, PVALID,
                                 derived_property)


class BaseClass(object):
    """ Abstract base class for all String classes in PRECIS framework.

    Subclasses must set `_allowed` to a tuple of derived property names.
    """
    _allowed = ()

    def __init__(self, ucd):
        self._ucd = ucd

    @property
    def ucd(self):
        """ Unicode character database.
        """
        return self._ucd

    def enforce(self, value, codec_name='precis'):
        """ Ensure that all characters in `value` are allowed by the string
        class.

        Return original `value` or raise a `UnicodeEncodeError`.
        """
        for i, char in enumerate(value):
            prop, kind = derived_property(ord(char), self.ucd)
            if prop in self._allowed:
                continue
            elif prop == CONTEXTJ and context_rule(value, i, self.ucd):
                continue
            elif prop == CONTEXTO and context_rule(value, i, self.ucd):
                continue
            raise UnicodeEncodeError(codec_name, value, i, i + 1,
                                     '%s/%s' % (prop, kind))
        return value


class IdentifierClass(BaseClass):
    """ Concrete class representing PRECIS IdentifierClass from RFC 7564.
    """
    _allowed = (PVALID,)


class FreeFormClass(BaseClass):
    """ Concrete class repsenting PRECIS FreeFormClass from RFC 7564.
    """
    _allowed = (PVALID, FREE_PVAL)
