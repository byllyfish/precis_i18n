"""Synthetic inputs and expected outcomes for the PRECIS benchmark."""

from collections import namedtuple
import sys


Case = namedtuple("Case", "name profile value expected old")
DIFFERING_OUTCOMES = frozenset(("reject-kelvin", "reject-uppercase-middle-dot"))
LONG_WORKLOAD_SAMPLES = {
    "context-katakana-16": 2400,
    "context-katakana-64": 512,
    "context-katakana-256": 192,
    "password-combining-1025": 1200,
    "context-arabic-64": 1200,
    "context-extended-arabic-64": 1200,
    "context-joiners-127": 1200,
}


def case(name, profile, value, expected, old=None):
    return Case(name, profile, value, expected, expected if old is None else old)


def cases():
    combining = "x" + "\u0315\u0300" * 512
    sorted_combining = "x" + "\u0300" * 512 + "\u0315" * 512
    result = [
        case("username-ascii", "UsernameCaseMapped", "User-42", "user-42"),
        case("username-unicode", "UsernameCaseMapped", "Élise-漢字", "élise-漢字"),
        case("username-width", "UsernameCaseMapped", "Ｕｓｅｒ４２", "user42"),
        case("username-katakana-width", "UsernameCaseMapped", "ｶﾞ", "ガ"),
        case("username-lowercase", "UsernameCaseMapped", "STRAẞE", "straße"),
        case("username-tolower-alias", "UsernameCaseMapped:ToLower", "STRAẞE", "straße"),
        case("username-casefold", "UsernameCaseMapped:CaseFold", "Straße", "strasse"),
        case("username-preserved", "UsernameCasePreserved", "Straße", "Straße"),
        case("username-nfc", "UsernameCasePreserved", "E\u0301clair", "Éclair"),
        case("username-mixed-script", "UsernameCaseMapped", "Αlpha漢字", "αlpha漢字"),
        case("password-opaque", "OpaqueString", "Ａ\u00a0Passe\u0301", "Ａ Passé"),
        case("password-combining-1025", "OpaqueString", combining, sorted_combining),
        case("nickname-mapped", "NicknameCaseMapped", "  Ａnna\u00a0  M.  ", "anna m."),
        case("nickname-tolower-alias", "NicknameCaseMapped:ToLower", "Straße", "straße"),
        case("nickname-casefold", "NicknameCaseMapped:CaseFold", "Straße", "strasse"),
        case("nickname-preserved", "NicknameCasePreserved", " Ａnna  M.　", "Anna M."),
        case("nickname-alias", "Nickname", "  Ａnna\u00a0  M.  ", "anna m."),
        case("identifier-class", "IdentifierClass", "Code-42", "Code-42"),
        case("freeform-class", "FreeFormClass", "User name", "User name"),
        case("reject-bidi", "UsernameCaseMapped", "aא", ("reject", "bidi_rule")),
        case("reject-password-control", "OpaqueString", "a\x00", ("reject", "controls")),
        case("reject-kelvin", "UsernameCaseMapped", "Kevin", ("reject", "has_compat"), "kevin"),
        case("reject-uppercase-middle-dot", "UsernameCaseMapped", "L·L",
             ("reject", "middle_dot"), "l·l"),
    ]
    result.extend(
        case("context-katakana-" + str(length), "IdentifierClass", "・" * (length - 1) + "カ",
             "・" * (length - 1) + "カ")
        for length in (16, 64, 256)
    )
    for name, symbol in (("context-arabic-64", "١"), ("context-extended-arabic-64", "۱")):
        value = symbol * 64
        result.append(case(name, "IdentifierClass", value, value))
    joiners = "ب\u200c" * 63 + "ب"
    result.append(case("context-joiners-127", "IdentifierClass", joiners, joiners))
    return result


if sys.version_info >= (3, 9):
    def execute(profile, value):
        try:
            return profile.enforce(value)
        except UnicodeEncodeError as error:
            return ("reject", error.reason.removeprefix("DISALLOWED/"))
else:
    def execute(profile, value):
        try:
            return profile.enforce(value)
        except UnicodeEncodeError as error:
            prefix = "DISALLOWED/"
            reason = error.reason
            return ("reject", reason[len(prefix):] if reason.startswith(prefix) else reason)
