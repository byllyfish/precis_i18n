import precis_codec.profile as _profile
import precis_codec.unicode as _unicode

__version__ = '0.1.1'

_ucd = _unicode.UnicodeData()

usernamecasemapped = _profile.UsernameCaseMapped(_ucd)
usernamecasepreserved = _profile.UsernameCasePreserved(_ucd)
opaquestring = _profile.OpaqueString(_ucd)
nickname = _profile.Nickname(_ucd)
