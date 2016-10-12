
import precis_i18n.baseclass as _base
import precis_i18n.profile as _profile
import precis_i18n.unicode as _unicode


_ucd = _unicode.UnicodeData()


def _factory(profile, **kwds):
    def construct():
        return profile(_ucd, **kwds)

    return construct


_profiles = {
    'identifierclass': _factory(_base.IdentifierClass, name='IdentifierClass'),
    'freeformclass': _factory(_base.FreeFormClass, name='FreeFormClass'),

    'usernamecasepreserved': _factory(_profile.Username, name='UsernameCasePreserved'),
    'usernamecasemapped': _factory(_profile.Username, name='UsernameCaseMapped', casemap='fold'),
    'usernamecasemapped:tolower': _factory(_profile.Username, name='UsernameCaseMapped:ToLower', casemap='lower'),

    'opaquestring': _factory(_profile.OpaqueString, name='OpaqueString'),

    'nicknamecasepreserved': _factory(_profile.Nickname, name='NicknameCasePreserved'),
    'nicknamecasemapped': _factory(_profile.Nickname, name='NicknameCaseMapped', casemap='fold'),
    'nicknamecasemapped:tolower': _factory(_profile.Nickname, name='NicknameCaseMapped:ToLower', casemap='lower'),

    # Alias for backward-compatibility with previous version of codec.
    'nickname': _factory(_profile.Nickname, name='Nickname', casemap='fold')
}


def get_profile(name):
    return _profiles[name.lower()]()
