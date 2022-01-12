"""
Program to check tables included in precis_i18n.unicode module.
"""

import re
from urllib.request import urlopen

import precis_i18n.unicode as ucd
from precis_i18n.codepointset import CodepointSet

PROP_REGEX = re.compile(rb"^([0-9A-Za-z.]+)\s+;\s+(\w+)\s+#")
DATAFILE_URLS = [
    "https://www.unicode.org/Public/UNIDATA/DerivedCoreProperties.txt",
    "https://www.unicode.org/Public/UNIDATA/extracted/DerivedJoiningType.txt#Join_Type",
    "https://www.unicode.org/Public/UNIDATA/Scripts.txt",
    'https://www.unicode.org/Public/UNIDATA/HangulSyllableType.txt#Hangul_Type',
]

def parse_unicode_datafile(url, props):
    if '#' in url:
        url, prop = url.split("#")
        prop += '='
    else:
        prop = ''

    for line in urlopen(url):
        m = PROP_REGEX.match(line)
        if m:
            codepoints, name = m.groups()
            props.setdefault('%s%s' % (prop, name.decode()), []).append(codepoints.decode())


def compare_codepoints(varname, codepoint_str):
    codepoints = CodepointSet(codepoint_str)
    if codepoints != getattr(ucd, varname):
        print(varname)
        print(codepoint_str)


def combine(props, *names):
    result = ''
    for name in names:
        cnt = len(CodepointSet(props[name]))
        result += '# %s (%d)\n%s\n' % (name, cnt, props[name])
    return result


def main():
    props = {}
    for url in DATAFILE_URLS:
        parse_unicode_datafile(url, props)

    for prop in props:
        props[prop] = '\n'.join(props[prop])

    compare_codepoints('_DEFAULT_IGNORABLE', props['Default_Ignorable_Code_Point'])
    compare_codepoints('_JOINTYPE_DUAL_JOINING', props['Join_Type=D'])
    compare_codepoints('_JOINTYPE_RIGHT_JOINING', props['Join_Type=R'])
    compare_codepoints('_JOINTYPE_LEFT_JOINING', props['Join_Type=L'])
    compare_codepoints('_JOINTYPE_TRANSPARENT', props['Join_Type=T'])
    compare_codepoints('_GREEK_SCRIPT', props['Greek'])
    compare_codepoints('_HEBREW_SCRIPT', props['Hebrew'])
    compare_codepoints('_HIRAGANA_KATAKANA_HAN', combine(props, 'Hiragana', 'Katakana', 'Han'))
    compare_codepoints('_OLD_HANGUL_JAMO', combine(props, 'Hangul_Type=L', 'Hangul_Type=V', 'Hangul_Type=T'))


if __name__ == '__main__':
    main()
