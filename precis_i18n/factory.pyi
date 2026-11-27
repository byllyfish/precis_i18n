from typing import Any, Dict, Optional, Union

from precis_i18n.baseclass import BaseClass
from precis_i18n.profile import Profile

_PROFILES = Dict[str, Union[BaseClass, Profile]]

def get_profile(
    name: str, *, unicodedata: Any = ..., unicode_version: Optional[str] = ...
) -> Profile: ...
