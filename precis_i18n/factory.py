"""Implements the `get_profile` factory function used to create profiles."""

import precis_i18n.baseclass as _base
import precis_i18n.profile as _profile
import precis_i18n.unicode as _unicode


def _factory(profile, **kwds):
    def _construct(ucd):
        return profile(ucd, **kwds)

    return _construct


_PROFILES = {
    "identifierclass": _factory(_base.IdentifierClass, name="IdentifierClass"),
    "freeformclass": _factory(_base.FreeFormClass, name="FreeFormClass"),
    "usernamecasepreserved": _factory(_profile.Username, name="UsernameCasePreserved"),
    "usernamecasemapped": _factory(
        _profile.Username, name="UsernameCaseMapped", casemap="lower"
    ),
    "usernamecasemapped_casefold": _factory(
        _profile.Username, name="UsernameCaseMapped:CaseFold", casemap="fold"
    ),
    "usernamecasemapped_tolower": _factory(
        _profile.Username, name="UsernameCaseMapped:ToLower", casemap="lower"
    ),
    "opaquestring": _factory(_profile.OpaqueString, name="OpaqueString"),
    "nicknamecasepreserved": _factory(_profile.Nickname, name="NicknameCasePreserved"),
    "nicknamecasemapped": _factory(
        _profile.Nickname, name="NicknameCaseMapped", casemap="lower"
    ),
    "nicknamecasemapped_casefold": _factory(
        _profile.Nickname, name="NicknameCaseMapped:CaseFold", casemap="fold"
    ),
    "nicknamecasemapped_tolower": _factory(
        _profile.Nickname, name="NicknameCaseMapped:ToLower", casemap="lower"
    ),
    # Alias for backward-compatibility with previous version of codec.
    "nickname": _factory(_profile.Nickname, name="Nickname", casemap="lower"),
}


def get_profile(name, *, unicodedata=None):
    """Return the desired PRECIS profile object.

    Choose name from:
        "IdentifierClass"
        "FreeFormClass"
        "UsernameCasePreserved"
        "UsernameCaseMapped"
        "UsernameCaseMapped:CaseFold"
        "UsernameCaseMapped:ToLower"
        "OpaqueString"
        "NicknameCasePreserved"
        "NicknameCaseMapped"
        "NicknameCaseMapped:CaseFold"
        "NicknameCaseMapped:ToLower"
        "Nickname" (alias for "NicknameCaseMapped")

    This function constructs a new profile each time; there is no cache.

    To use an alternative Unicode implementation, pass a module or object that
    implements the unicodedata interface via the unicodedata keyword argument.
    The default is to use the unicodedata module built into the Python runtime.

    Args:
        name (str): name of a PRECIS profile
        unicodedata (module|object): Alternative unicodedata interface

    Returns:
        AbstractProfile: PRECIS profile object.

    Raises:
        KeyError: Profile not found.
    """
    profile = name.lower().replace(":", "_")
    return _PROFILES[profile](_unicode.UnicodeData(unicodedata))
