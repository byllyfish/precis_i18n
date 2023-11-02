from typing import NoReturn, Optional, Tuple

from precis_i18n.unicode import UnicodeData

class BaseClass:
    ucd: UnicodeData
    name: str

    def __init__(self, ucd: UnicodeData, name: str = ...) -> None: ...
    def enforce(self, value: str, codec_name: Optional[str] = ...) -> str: ...

class IdentifierClass(BaseClass):
    _allowed: Tuple[str]

class FreeFormClass(BaseClass):
    _allowed: Tuple[str, str]

def raise_error(encoding: str, value: str, offset: int, error: str) -> NoReturn: ...
