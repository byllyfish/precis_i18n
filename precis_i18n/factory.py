"""
Implements the `get_profile` factory function used to create profiles by name.
"""

import precis_i18n.baseclass as _base
import precis_i18n.profile as _profile
import precis_i18n.unicode as _unicode

UCD = _unicode.UnicodeData()


def _factory(profile, **kwds):
    def _construct():
        return profile(UCD, **kwds)

    return _construct


_PROFILES = {
    'identifierclass': _factory(
        _base.IdentifierClass, name='IdentifierClass'),
    'freeformclass': _factory(
        _base.FreeFormClass, name='FreeFormClass'),
    'usernamecasepreserved': _factory(
        _profile.Username, name='UsernameCasePreserved'),
    'usernamecasemapped': _factory(
        _profile.Username, name='UsernameCaseMapped', casemap='fold'),
    'usernamecasemapped:tolower': _factory(
        _profile.Username, name='UsernameCaseMapped:ToLower', casemap='lower'),
    'opaquestring': _factory(
        _profile.OpaqueString, name='OpaqueString'),
    'nicknamecasepreserved': _factory(
        _profile.Nickname, name='NicknameCasePreserved'),
    'nicknamecasemapped': _factory(
        _profile.Nickname, name='NicknameCaseMapped', casemap='fold'),
    'nicknamecasemapped:tolower': _factory(
        _profile.Nickname, name='NicknameCaseMapped:ToLower', casemap='lower'),

    # Alias for backward-compatibility with previous version of codec.
    'nickname': _factory(
        _profile.Nickname, name='Nickname', casemap='fold')
}


def get_profile(name):
    """Return the desired PRECIS profile object.

    Choose name from:
        "IdentifierClass"
        "FreeFormClass"
        "UsernameCasePreserved"
        "UsernameCaseMapped"
        "UsernameCaseMapped:ToLower"
        "OpaqueString"
        "NicknameCasePreserved"
        "NicknameCaseMapped"
        "NicknameCaseMapped:ToLower"
        "Nickname" (alias for "NicknameCaseMapped")

    This function constructs a new profile each time; there is no cache.

    Args:
        name (str): name of a PRECIS profile

    Returns:
        AbstractProfile: PRECIS profile object.
    """
    return _PROFILES[name.lower()]()
