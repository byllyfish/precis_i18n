from typing import Set

from precis_i18n.unicode import UnicodeData

_LTR_FIRST = Set[str]
_LTR_ALLOWED = Set[str]
_LTR_LAST = Set[str]
_LTR_EXCL = Set[str]
_RTL_FIRST = Set[str]
_RTL_ALLOWED = Set[str]
_RTL_LAST = Set[str]
_RTL_EXCL = Set[str]
_RTL_ANY = Set[str]

def bidi_rule(value: str, ucd: UnicodeData) -> bool: ...
def has_rtl(value: str, ucd: UnicodeData) -> bool: ...
