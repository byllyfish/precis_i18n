"""
Implements the PRECIS profile classes.
"""

import re

from precis_i18n.baseclass import FreeFormClass, IdentifierClass
from precis_i18n.bidi import bidi_rule, has_rtl


class Profile(object):
    """
    Abstract base class for a PRECIS profile.

    Subclasses should override the `*_rule` methods.
    """

    def __init__(self, base, name, casemap=None):
        self._base = base
        self._name = name
        # casemap can be either None, 'fold', or 'lower'.
        if casemap is None:
            self._casemap = None
        elif casemap == 'fold':
            self._casemap = _casefold
        elif casemap == 'lower':
            self._casemap = _caselower
        else:
            raise ValueError('Unknown casemap value: %s' % casemap)

    @property
    def base(self):
        """ The profile's base string instance.
        """
        return self._base

    @property
    def name(self):
        """ The profile's name.
        """
        return self._name

    def enforce(self, value):
        """ Enforce the profile.
        """
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
        return self.base.enforce(temp, self.name)

    def width_mapping_rule(self, value):
        return value

    def additional_mapping_rule(self, value):
        return value

    def case_mapping_rule(self, value):
        if self._casemap:
            return self._casemap(value)
        return value

    def normalization_rule(self, value):
        return self.base.ucd.normalize('NFC', value)

    def directionality_rule(self, value):
        return value


class Username(Profile):
    """
    Name:  UsernameCasePreserved | UsernameCaseMapped

    Base Class:  IdentifierClass.
    
    Applicability:  Usernames in security and application protocols.
    
    Replaces:  The SASLprep profile of stringprep.
    
    Width-Mapping Rule:  Map fullwidth and halfwidth characters to their
       decomposition mappings.
    
    Additional Mapping Rule:  None.
    
    Case-Mapping Rule:  None | Map uppercase and titlecase characters to
       lowercase.
    
    Normalization Rule:  NFC.
    
    Directionality Rule:  The "Bidi Rule" defined in RFC 5893 applies.
    
    Enforcement:  To be defined by security or application protocols that
       use this profile.
    
    Specification:  RFC7613, Section 3.3. 
    """

    def __init__(self, ucd, name, casemap=None):
        super().__init__(IdentifierClass(ucd), name, casemap)

    def width_mapping_rule(self, value):
        return self.base.ucd.width_map(value)

    def directionality_rule(self, value):
        # Only apply the "bidi rule" if the string contains RTL characters.
        if has_rtl(value, self.base.ucd):
            if not bidi_rule(value, self.base.ucd):
                raise UnicodeEncodeError(self.name, value, 0, len(value),
                                         'bidi rule')
        return value


class OpaqueString(Profile):
    """
    Name:  OpaqueString.

    Base Class:  FreeformClass.

    Applicability:  Passwords and other opaque strings in security and
       application protocols.

    Replaces:  The SASLprep profile of stringprep.

    Width-Mapping Rule:  None.

    Additional Mapping Rule:  Map non-ASCII space characters to ASCII
       space.

    Case-Mapping Rule:  None.

    Normalization Rule:  NFC.

    Directionality Rule:  None.

    Enforcement:  To be defined by security or application protocols that
       use this profile.

    Specification:  RFC7613, Section 4.2.
    """

    def __init__(self, ucd, name):
        super().__init__(FreeFormClass(ucd), name, casemap=None)

    def additional_mapping_rule(self, value):
        return self.base.ucd.map_nonascii_space_to_ascii(value)


class Nickname(Profile):
    """
    Name:  Nickname.
 
    Base Class:  FreeformClass.
 
    Applicability:  Nicknames in messaging and text conferencing
       technologies; petnames for devices, accounts, and people; and
       other uses of nicknames or petnames.
 
    Replaces:  None.
 
    Width Mapping Rule:  None (handled via NFKC).
 
    Additional Mapping Rule:  Map non-ASCII space characters to ASCII
       space, strip leading and trailing space characters, map interior
       sequences of multiple space characters to a single ASCII space.
 
    Case Mapping Rule:  Map uppercase and titlecase characters to
       lowercase using Unicode Default Case Folding.
 
    Normalization Rule:  NFKC.
 
    Directionality Rule:  None.
 
    Enforcement:  To be specified by applications.
 
    Specification:  RFC7700
    """

    def __init__(self, ucd, name, casemap=None):
        super().__init__(FreeFormClass(ucd), name, casemap)

    def additional_mapping_rule(self, value):
        temp = self.base.ucd.map_nonascii_space_to_ascii(value)
        return re.sub(r'  +', ' ', temp.strip())

    def normalization_rule(self, value):
        return self.base.ucd.normalize('NFKC', value)


def _casefold(s):
    return s.casefold()


def _caselower(s):
    return s.lower()
