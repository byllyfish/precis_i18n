"""Verify an installed Unicode provider and PRECIS tables against official UCD files."""

import argparse
import hashlib
import json
import locale
import re
import sys
from pathlib import Path

from generate_unicode_data import VERSIONS, verified_directory

SCALAR_END = 0x110000
FORMS = ("NFC", "NFD", "NFKC", "NFKD")


def _records(source):
    for line in source.splitlines():
        row = line.partition("#")[0].strip()
        if row and not row.startswith("@"):
            yield [cell.strip() for cell in row.split(";")]


def _string(cps):
    return "".join(chr(int(cp, 16)) for cp in cps.split())


def _digits(field):
    start, _, end = field.partition("..")
    return range(int(start, 16), int(end or start, 16) + 1)


def verify_normalization(ucd, files):
    count = 0
    for row in _records(files["NormalizationTest.txt"]):
        c1, c2, c3, c4, c5 = map(_string, row[:5])
        actual = tuple(tuple(ucd.normalize(form, x) for x in (c1, c2, c3, c4, c5)) for form in FORMS)
        assert actual == (
            (c2, c2, c2, c4, c4), (c3, c3, c3, c5, c5), (c4,) * 5, (c5,) * 5,
        ), "normalization row {}".format(count + 1)
        count += 1
    return count


def _mapping_oracles(files):
    width = {}
    lowercase = {}
    for row in _records(files["UnicodeData.txt"]):
        cp = int(row[0], 16)
        if row[5].startswith(("<wide>", "<narrow>")):
            width[cp] = _string(row[5].split(" ", 1)[1])
        if row[13]:
            lowercase[cp] = _string(row[13])
    for row in _records(files["SpecialCasing.txt"]):
        if not row[4]:
            lowercase[int(row[0], 16)] = _string(row[1])

    fold = {}
    for row in _records(files["CaseFolding.txt"]):
        if row[1] in ("C", "F"):
            fold[int(row[0], 16)] = _string(row[2])
    return width, lowercase, fold


def verify_mappings(ucd, files):
    expected_maps = _mapping_oracles(files)
    for apply, expected in zip((ucd.width_map, ucd.lower, ucd.casefold), expected_maps):
        for cp in range(SCALAR_END):
            source = chr(cp)
            expected_value = expected.get(cp, source)
            assert apply(source) == expected_value, "{} U+{:04X}".format(apply.__name__, cp)

    # Default lowercase ignores intervening Case_Ignorable code points even
    # when they are also Cased, as with U+0345.
    contextual = (
        ("\u0130", "i\u0307"), ("I\u0131", "i\u0131"),
        ("AΣ", "aς"), ("AΣΣ", "aσς"), ("AΣA", "aσa"), ("Σ", "σ"),
        ("A\u0301Σ\u0301", "a\u0301ς\u0301"),
        ("A\u0301Σ\u0301A", "a\u0301σ\u0301a"),
        ("\u0345Σ", "\u0345σ"),
        ("A\u0345Σ\u0345", "a\u0345ς\u0345"),
        ("A\u0345Σ\u0345A", "a\u0345σ\u0345a"), ("AΣ+A", "aς+a"),
        ("Ɤ", "ɤ"), ("\ua7ce", "\ua7cf"),
    )
    for original, expected in contextual:
        assert ucd.lower(original) == expected, original.encode("unicode_escape")
    return [len(mapping) for mapping in expected_maps] + [len(contextual)]


def _provider_properties(files):
    expected = {}
    start = None
    for row in _records(files["UnicodeData.txt"]):
        cp = int(row[0], 16)
        properties = row[2], int(row[3]), row[4]
        if row[1].endswith(", First>"):
            start = cp
        elif row[1].endswith(", Last>"):
            assert start is not None
            for point in range(start, cp + 1):
                expected[point] = properties
            start = None
        else:
            expected[cp] = properties
    assert start is None
    return expected


def _classification(path):
    expected = {}
    expression = re.compile(r"^([0-9A-F]+)-([0-9A-F]+) ([A-Z_]+)/[a-z0-9_]+$")
    last = -1
    with path.open(encoding="ascii") as source:
        for row in source:
            match = expression.fullmatch(row.strip())
            assert match, "invalid derived property row"
            lo, hi, prop = match.groups()
            start, end = int(lo, 16), int(hi, 16)
            assert start == last + 1 and start <= end
            for point in range(start, end + 1):
                expected[point] = prop
            last = end
    assert last + 1 == SCALAR_END
    return expected


def _sets(source):
    indexed = {}
    for row in _records(source):
        indexed.setdefault(row[1], set()).update(_digits(row[0]))
    return indexed


def verify_properties(ucd, files, classifier, classification):
    expected_props = _provider_properties(files)
    expected_precis = _classification(classification)
    core = _sets(files["DerivedCoreProperties.txt"])
    joining = _sets(files["DerivedJoiningType.txt"])
    scripts = _sets(files["Scripts.txt"])
    hangul = _sets(files["HangulSyllableType.txt"])
    joins = {cp: kind for kind in "DRLT" for cp in joining[kind]}
    compared = (
        (ucd.old_hangul_jamo, hangul["L"] | hangul["V"] | hangul["T"]),
        (ucd.default_ignorable, core["Default_Ignorable_Code_Point"]),
        (ucd.greek_script, scripts["Greek"]),
        (ucd.hebrew_script, scripts["Hebrew"]),
        (ucd.hiragana_katakana_han_script, scripts["Hiragana"] | scripts["Katakana"] | scripts["Han"]),
    )
    for cp in range(SCALAR_END):
        char = chr(cp)
        category, combining, bidi = expected_props.get(cp, ("Cn", 0, None))
        assert (ucd.category(char), ucd.combining(char)) == (category, combining), "UCD U+{:04X}".format(cp)
        # Some provider APIs report a default bidi value for unassigned code
        # points. PRECIS excludes those points before evaluating bidi rules.
        if bidi is not None:
            assert ucd.bidirectional(char) == bidi, "bidi U+{:04X}".format(cp)
        assert classifier(cp, ucd)[0] == expected_precis[cp], "PRECIS U+{:04X}".format(cp)
        for method, points in compared:
            assert method(cp) == (cp in points), "{} U+{:04X}".format(method.__name__, cp)
        assert ucd._join_type(cp) == joins.get(cp), "joining type U+{:04X}".format(cp)
    return SCALAR_END


def _outcome(prepare, value):
    try:
        return prepare(value).hex()
    except UnicodeEncodeError as error:
        return ("reject", error.start, error.end, error.reason)


def _digest(rows):
    return hashlib.sha256(json.dumps(rows, ensure_ascii=True).encode("ascii")).hexdigest()


def profile_digest(factory, identify, provider, version):
    profiles = (
        "IdentifierClass", "FreeFormClass", "UsernameCasePreserved", "UsernameCaseMapped",
        "UsernameCaseMapped:CaseFold", "UsernameCaseMapped:ToLower", "OpaqueString",
        "NicknameCasePreserved", "NicknameCaseMapped", "NicknameCaseMapped:CaseFold",
        "NicknameCaseMapped:ToLower", "Nickname",
    )
    values = (
        "ALICE", "Ａlice", "a\u0301", "Á", "Straße", "STRASSE", "l·l", "L·L",
        "Kevin", "ΣΣ", "Σ\u0345Σ\u0345", "\u0130", "\u0131I", "\ua7cb", "\ua7ce",
        "\u05c8", "\U00010400", "Ａ\u2003E\u0301", "\u0645\u200c\u0645",
        "\u05d0\u05f3", "\u0375\u03b1", "\u30fbカ", "ﾡￂ", "ｶﾞ", "\u0301",
        "\u200d", "\u0600", "\ud800", "", "  Ｆoo\u3000 BAR  ", " \u200b",
    )
    outcomes = []
    identities = []
    comparison_count = 0
    for name in profiles:
        profile = factory(name, unicodedata=provider, unicode_version=version)
        identity = identify(profile)
        assert identity.fingerprint is not None and identity.unicode_version == version
        identities.append((name, identity.fingerprint))
        key = getattr(profile, "comparison_key", None)
        for value in values:
            outcome = _outcome(lambda text: profile.enforce(text).encode("utf-8"), value)
            comparison = None if key is None else _outcome(key, value)
            comparison_count += key is not None
            outcomes.append((name, outcome, comparison))
    return len(profiles) * len(values), comparison_count, _digest(outcomes), _digest(identities)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", choices=VERSIONS)
    parser.add_argument("ucd_directory", type=Path)
    parser.add_argument("classification", type=Path)
    parser.add_argument("--source", type=Path, help="explicit source checkout for source qualification")
    args = parser.parse_args()
    if args.source is not None:
        sys.path.insert(0, str(args.source.resolve()))

    import unicodedata2

    from precis_i18n import get_profile, get_profile_identity
    from precis_i18n.derived import derived_property
    from precis_i18n.unicode import UnicodeData

    files = verified_directory(args.version, args.ucd_directory)
    ucd = UnicodeData(unicodedata2, unicode_version=args.version)
    nfc = verify_normalization(ucd, files)
    widths, lowercase, casefold, contextual = verify_mappings(ucd, files)
    classifications = verify_properties(ucd, files, derived_property, args.classification)
    profile_cases, comparisons, outcome_hash, identity_hash = profile_digest(
        get_profile, get_profile_identity, unicodedata2, args.version
    )
    print(json.dumps({
        "runtime": sys.version,
        "locale": locale.setlocale(locale.LC_CTYPE, ""),
        "unicode": args.version,
        "data_identity": ucd.data_identity,
        "normalization_rows_for_each_form": nfc,
        "width_mappings": widths,
        "lowercase_mappings": lowercase,
        "casefold_mappings": casefold,
        "contextual_lowercase_cases": contextual,
        "checked_code_points": classifications,
        "profile_cases": profile_cases,
        "comparison_cases": comparisons,
        "profile_outcome_sha256": outcome_hash,
        "profile_identity_sha256": identity_hash,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
