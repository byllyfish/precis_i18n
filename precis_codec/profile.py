import re

from precis_codec.baseclass import FreeFormClass, IdentifierClass
from precis_codec.bidi import bidi_rule, has_rtl


class Profile(object):
    def __init__(self, base, name):
        self._base = base
        self._name = name

    @property
    def base(self):
        return self._base

    @property
    def name(self):
        return self._name

    def enforce(self, value):
        # If we get called with a byte string, decode it first.
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        elif not isinstance(value, str):
            raise ValueError('not a string')
        # Apply the five rules in order specified by RFC 7564.
        temp = self.width_mapping_rule(value)
        temp = self.additional_mapping_rule(temp)
        temp = self.case_mapping_rule(temp)
        temp = self.normalization_rule(temp)
        temp = self.directionality_rule(temp)
        # Make sure the resulting value is not empty.
        if not temp:
            raise UnicodeEncodeError(self.name, temp, 0, 1, 'empty')
        # Apply behavioral rules from the base string class last.
        temp = self.base.enforce(temp, self.name)
        # Return byte string encoded in utf-8.
        return temp.encode('utf-8')

    def width_mapping_rule(self, value):
        return value

    def additional_mapping_rule(self, value):
        return value

    def case_mapping_rule(self, value):
        return value

    def normalization_rule(self, value):
        return self.base.ucd.normalize('NFC', value)

    def directionality_rule(self, value):
        return value


class UsernamePreserved(Profile):
    def __init__(self, ucd, name='UsernamePreserved'):
        super().__init__(IdentifierClass(ucd), name)

    def width_mapping_rule(self, value):
        return self.base.ucd.width_map(value)

    def directionality_rule(self, value):
        # Only apply the "bidi rule" if the string contains RTL characters.
        if has_rtl(value, self.base.ucd):
            if not bidi_rule(value, self.base.ucd):
                raise UnicodeEncodeError(self.name, value, 0, len(value),
                                         'bidi rule')
        return value


class UsernameCaseMapped(UsernamePreserved):
    def __init__(self, ucd, name='UsernameCaseMapped'):
        super().__init__(ucd, name)

    def case_mapping_rule(self, value):
        return value.casefold()


class OpaqueString(Profile):
    def __init__(self, ucd, name='OpaqueString'):
        super().__init__(FreeFormClass(ucd), name)


class NicknamePreserved(Profile):
    def __init__(self, ucd, name='NicknamePreserved'):
        super().__init__(FreeFormClass(ucd), name)

    def additional_mapping_rule(self, value):
        temp = self.base.ucd.replace_whitespace(value).strip()
        return re.sub(r'  +', temp, ' ')

    def normalization_rule(self, value):
        return self.base.ucd.normalize('NFKC', value)


class NicknameCaseMapped(NicknamePreserved):
    def __init__(self, ucd, name='NicknameCaseMapped'):
        super().__init__(ucd, name)

    def case_mapping_rule(self, value):
        return value.casefold()
