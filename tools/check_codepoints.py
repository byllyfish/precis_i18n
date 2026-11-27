"""
Program to check bundled ranges against their pinned Unicode data.
"""

import hashlib
import json
import re
from urllib.request import urlopen

from generate_unicode_data import SOURCES

from precis_i18n._unicode_tables import CURRENT, load
from precis_i18n.codepointset import CodepointSet

PROP_REGEX = re.compile(rb"^([0-9A-Za-z.]+)\s+;\s+(\w+)\s+#")
FILES = (
    ("DerivedCoreProperties.txt", ""),
    ("DerivedJoiningType.txt", "Join_Type="),
    ("Scripts.txt", ""),
    ("HangulSyllableType.txt", "Hangul_Type="),
)


def parse_unicode_datafile(receipt, prop, props):
    with urlopen(receipt["url"], timeout=30) as response:
        source = response.read()
    if hashlib.sha256(source).hexdigest() != receipt["sha256"]:
        raise ValueError("Unicode source hash mismatch")
    for line in source.splitlines():
        m = PROP_REGEX.match(line)
        if m:
            codepoints, name = m.groups()
            props.setdefault("%s%s" % (prop, name.decode()), []).append(
                codepoints.decode()
            )


def compare_codepoints(varname, codepoint_str):
    codepoints = CodepointSet(codepoint_str)
    if codepoints != load(CURRENT).ranges[varname]:
        print(varname)
        print(codepoint_str)


def combine(props, *names):
    result = ""
    for name in names:
        cnt = len(CodepointSet(props[name]))
        result += "# %s (%d)\n%s\n" % (name, cnt, props[name])
    return result


def main():
    props = {}
    inputs = json.loads(SOURCES.read_text(encoding="ascii"))[CURRENT]
    for filename, prop in FILES:
        parse_unicode_datafile(inputs[filename], prop, props)

    for prop in props:
        props[prop] = "\n".join(props[prop])

    compare_codepoints("default_ignorable", props["Default_Ignorable_Code_Point"])
    compare_codepoints("dual_joining", props["Join_Type=D"])
    compare_codepoints("right_joining", props["Join_Type=R"])
    compare_codepoints("left_joining", props["Join_Type=L"])
    compare_codepoints("transparent_joining", props["Join_Type=T"])
    compare_codepoints("greek", props["Greek"])
    compare_codepoints("hebrew", props["Hebrew"])
    compare_codepoints(
        "hiragana_katakana_han", combine(props, "Hiragana", "Katakana", "Han")
    )
    compare_codepoints(
        "jamo",
        combine(props, "Hangul_Type=L", "Hangul_Type=V", "Hangul_Type=T"),
    )


if __name__ == "__main__":
    main()
