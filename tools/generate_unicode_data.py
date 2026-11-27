"""Generate the versioned PRECIS tables from checksum-pinned UCD files."""

import argparse
import hashlib
import json
from pathlib import Path

SOURCES = Path(__file__).with_name("unicode_sources.json")
VERSIONS = ("17.0.0", "18.0.0")


def verified_directory(version, directory):
    """Return verified UCD source text keyed by its local filename."""
    all_sources = json.loads(SOURCES.read_text(encoding="ascii"))
    result = {}
    for name, receipt in all_sources[version].items():
        payload = (directory / name).read_bytes()
        if hashlib.sha256(payload).hexdigest() != receipt["sha256"]:
            raise ValueError("Checksum mismatch for {} {}".format(version, name))
        result[name] = payload.decode("utf-8")
    return result


def _rows(contents):
    for line in contents.splitlines():
        content = line.split("#", 1)[0].strip()
        if content:
            yield tuple(field.strip() for field in content.split(";"))


def _point_range(source):
    start, _, end = source.partition("..")
    return int(start, 16), int(end or start, 16)


def _ranges(contents, names):
    return sorted(
        _point_range(row[0]) for row in _rows(contents) if row[1] in names
    )


def _codepoints(field):
    return [int(item, 16) for item in field.split()]


def _character_mappings(text):
    width, lower, spaces = {}, {}, {}
    for row in _rows(text):
        codepoint = int(row[0], 16)
        parts = row[5].split()
        if parts and parts[0] in {"<wide>", "<narrow>"}:
            mapping, = _codepoints(" ".join(parts[1:]))
            width[codepoint] = mapping
        if row[13]:
            lower[codepoint] = _codepoints(row[13])
        if row[2] == "Zs" and codepoint != 0x20:
            spaces[codepoint] = 0x20
    return width, lower, spaces


def _case_mappings(lower, special_casing, casefolding):
    context = {}
    for row in _rows(special_casing):
        codepoint = int(row[0], 16)
        mapping = _codepoints(row[1])
        condition = row[4]
        if not condition:
            lower[codepoint] = mapping
        elif condition == "Final_Sigma":
            context["final_sigma"] = [codepoint, mapping]
        elif not set(condition.split()).intersection({"lt", "tr", "az"}):
            raise ValueError("Unrecognized default lowercase condition: " + condition)

    fold = {int(row[0], 16): _codepoints(row[2]) for row in _rows(casefolding) if row[1] in {"C", "F"}}
    if "final_sigma" not in context:
        raise ValueError("SpecialCasing.txt has no final sigma")
    return fold, context


def _property_ranges(files):
    core, scripts, joining = (files[name] for name in (
        "DerivedCoreProperties.txt", "Scripts.txt", "DerivedJoiningType.txt"
    ))
    return {
        "cased": _ranges(core, {"Cased"}),
        "case_ignorable": _ranges(core, {"Case_Ignorable"}),
        "default_ignorable": _ranges(core, {"Default_Ignorable_Code_Point"}),
        "greek": _ranges(scripts, {"Greek"}),
        "hebrew": _ranges(scripts, {"Hebrew"}),
        "hiragana_katakana_han": _ranges(scripts, {"Hiragana", "Katakana", "Han"}),
        "jamo": _ranges(files["HangulSyllableType.txt"], {"L", "V", "T"}),
        "dual_joining": _ranges(joining, {"D"}),
        "left_joining": _ranges(joining, {"L"}),
        "right_joining": _ranges(joining, {"R"}),
        "transparent_joining": _ranges(joining, {"T"}),
    }


def build_tables(version, directory):
    files = verified_directory(version, directory)
    width, lower, spaces = _character_mappings(files["UnicodeData.txt"])
    fold, context = _case_mappings(lower, files["SpecialCasing.txt"], files["CaseFolding.txt"])
    return {
        "version": version,
        "width": width,
        "lower": lower,
        "fold": fold,
        "spaces": spaces,
        "context": context,
        "ranges": _property_ranges(files),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path, help="directory with the pinned version subdirectories")
    parser.add_argument("output", type=Path, help="write generated package data to this directory")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for version in VERSIONS:
        tables = build_tables(version, args.inputs / version)
        output = args.output / "_unicode_{}.json".format(version.split(".", 1)[0])
        payload = json.dumps(tables, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        output.write_bytes(payload.encode("ascii"))


if __name__ == "__main__":
    main()
