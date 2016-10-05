"""
precis_i18n
"""

import precis_i18n.profile as _profile
import precis_i18n.unicode as _unicode

__version__ = '0.2.0'

_ucd = _unicode.UnicodeData()

usernamecasemapped = _profile.UsernameCaseMapped(_ucd)
usernamecasepreserved = _profile.UsernameCasePreserved(_ucd)
opaquestring = _profile.OpaqueString(_ucd)
nickname = _profile.Nickname(_ucd)
