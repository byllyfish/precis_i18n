from typing import Any
from typing import Optional
from typing import Tuple
from typing import NoReturn


class BaseClass:

    def __init__(self, ucd: Any, name: str = ...) -> None:
        ...
    
    def enforce(self, value: str, codec_name: Optional[str] = ...) -> str:
        ...
    

class IdentifierClass(BaseClass):

    _allowed = Tuple[str]


class FreeFormClass(BaseClass):

    _allowed = Tuple[str, str]


def raise_error(encoding: str, value: str, offset: int, error: str) -> NoReturn:
    ...
