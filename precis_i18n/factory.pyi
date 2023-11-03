from typing import Dict, Union

from precis_i18n.baseclass import BaseClass
from precis_i18n.profile import Profile
from precis_i18n.unicode import UnicodeData

_PROFILES = Dict[str, Union[BaseClass, Profile]]

def get_profile(name: str, *, unicodedata: UnicodeData = ...) -> Profile: ...
