from precis_i18n.unicode import UnicodeData


def context_rule_error(value: str, offset: int, ucd: UnicodeData) -> str:
    ...

def rule_zero_width_nonjoiner(value: str, offset: int, ucd: UnicodeData) -> bool:
    ...

def rule_zero_width_joiner(value: str, offset: int, ucd: UnicodeData) -> bool:
    ...

def rule_middle_dot(value: str, offset: int, ucd: UnicodeData) -> bool:
    ...

def rule_greek_keraia(value: str, offset: int, ucd: UnicodeData) -> bool:
    ...

def rule_hebrew_punctuation(value: str, offset: int, ucd: UnicodeData) -> bool:
    ...

def rule_katakana_middle_dot(value: str, offset: int, ucd: UnicodeData) -> bool:
    ...

def rule_arabic_indic(value: str, offset: int, ucd: UnicodeData) -> bool:
    ...

def rule_extended_arabic_indic(value: str, offset: int, ucd: UnicodeData) -> bool:
    ...

_RULES = ...
