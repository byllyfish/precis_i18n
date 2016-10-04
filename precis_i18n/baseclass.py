from precis_i18n.context import context_rule
from precis_i18n.derived import (CONTEXTJ, CONTEXTO, FREE_PVAL, PVALID,
                                  derived_property)


class BaseClass(object):
    def __init__(self, ucd):
        self._ucd = ucd

    @property
    def ucd(self):
        return self._ucd

    def _enforce(self, value, codec_name, *allowed):
        """ Ensure that all characters in `value` are allowed by the string
        class.

        Return original `value` or raise a `UnicodeEncodeError`.
        """
        for i, char in enumerate(value):
            prop, kind = derived_property(ord(char), self.ucd)
            if prop in allowed:
                continue
            elif prop == CONTEXTJ and context_rule(value, i, self.ucd):
                continue
            elif prop == CONTEXTO and context_rule(value, i, self.ucd):
                continue
            raise UnicodeEncodeError(codec_name, value, i, i + 1,
                                     '%s/%s' % (prop, kind))
        return value


class IdentifierClass(BaseClass):
    def enforce(self, value, codec_name='precis-identifier'):
        return self._enforce(value, codec_name, PVALID)


class FreeFormClass(BaseClass):
    def enforce(self, value, codec_name='precis-freeform'):
        return self._enforce(value, codec_name, PVALID, FREE_PVAL)
