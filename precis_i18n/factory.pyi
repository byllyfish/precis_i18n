from typing import Any
from typing import Dict

from precis_i18n.profile import Profile

_PROFILES = Dict[str, Any]

def get_profile(name: str, *, unicodedata: Any = ...) -> Profile:
    ...
