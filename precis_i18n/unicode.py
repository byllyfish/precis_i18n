"""
Implements the UnicodeData class.
"""

import re
import unicodedata

from precis_i18n.codepointset import CodepointSet


def _version_to_float(version):
    m = re.match(r'^([0-9]+\.[0-9]+)\.[0-9]+$', version)
    if not m:
        raise ValueError('Unexpected unicode version format: %s' % version)
    return float(m.group(1))


class UnicodeData(object):
    """
    Adapter for Python's built-in unicodedata module.

    This class extends the unicodedata module for use in PRECIS profiles.
    """

    _halfwidth_chars = re.compile(r'[\uff01-\uffef]')
    _space_chars = re.compile(r'[\u00a0\u1680\u2000-\u200A\u202F\u205F\u3000]')

    def __init__(self, ucd=unicodedata):
        self._ucd = ucd
        self._version = _version_to_float(ucd.unidata_version)

    @property
    def version(self):
        return self._version

    # These methods call through to the underlying unicodedata object.

    def category(self, char):
        return self._ucd.category(char)

    def combining(self, char):
        return self._ucd.combining(char)

    def bidirectional(self, char):
        return self._ucd.bidirectional(char)

    def normalize(self, form, value):
        return self._ucd.normalize(form, value)

    def width_map(self, value):
        """ Map half-width and full-width chars to their compat equivs.
        """
        def decompose(m):
            char = m.group(0)
            assert len(char) == 1
            norm = self._ucd.normalize('NFKC', char)
            return norm if len(norm) == 1 else char

        return self._halfwidth_chars.sub(decompose, value)

    def map_nonascii_space_to_ascii(self, value):
        """ Convert non-ASCII white space {Zs} to ASCII ' '.
        """
        return self._space_chars.sub(' ', value)

    def default_ignorable(self, cp):
        return cp in _DEFAULT_IGNORABLE

    def has_compat(self, cp):
        char = chr(cp)
        norm = self.normalize('NFKC', char)
        assert len(norm) > 0
        return norm != char

    def control(self, cp):
        return (0x00 <= cp <= 0x1f) or (0x7f <= cp <= 0x9f)

    def noncharacter(self, cp):
        last = cp & 0x0000ffff
        return (0xfffe <= last <= 0xffff) or (0xfdd0 <= cp <= 0xfdef)

    def old_hangul_jamo(self, cp):
        return cp in _OLD_HANGUL_JAMO

    def greek_script(self, cp):
        return cp in _GREEK_SCRIPT

    def hebrew_script(self, cp):
        return cp in _HEBREW_SCRIPT

    def hiragana_katakana_han_script(self, cp):
        return cp in _HIRAGANA_KATAKANA_HAN

    def combining_virana(self, cp):
        return self.combining(chr(cp)) == 9

    def arabic_indic(self, cp):
        return 0x0660 <= cp <= 0x0669

    def extended_arabic_indic(self, cp):
        return 0x06f0 <= cp <= 0x06f9

    def valid_jointype(self, value, offset):
        assert 0x200c <= ord(value[offset]) <= 0x200d
        return self._scan_join(reversed(value[:offset]), 'L') and \
                self._scan_join(value[offset + 1:], 'R')

    def _scan_join(self, iterable, term):
        for char in iterable:
            jt = self._join_type(ord(char))
            if jt == term or jt == 'D':
                return True
            if jt != 'T':
                return False
        return False

    def _join_type(self, cp):
        if cp in _JOINTYPE_DUAL_JOINING:
            return 'D'
        elif cp in _JOINTYPE_RIGHT_JOINING:
            return 'R'
        elif cp in _JOINTYPE_LEFT_JOINING:
            return 'L'
        elif cp in _JOINTYPE_TRANSPARENT:
            return 'T'
        return None

# http://www.unicode.org/Public/9.0.0/ucd/DerivedCoreProperties.txt
# Derived Property: Default_Ignorable_Code_Point
_DEFAULT_IGNORABLE = CodepointSet('''
00AD
034F
061C
115F..1160
17B4..17B5
180B..180D
180E
200B..200F
202A..202E
2060..2064
2065
2066..206F
3164
FE00..FE0F
FEFF
FFA0
FFF0..FFF8
1BCA0..1BCA3
1D173..1D17A
E0000
E0001
E0002..E001F
E0020..E007F
E0080..E00FF
E0100..E01EF
E01F0..E0FFF
''')

# http://www.unicode.org/Public/9.0.0/ucd/extracted/DerivedJoiningType.txt
# Joining_Type=Dual_Joining
_JOINTYPE_DUAL_JOINING = CodepointSet('''
0620
0626
0628
062A..062E
0633..063F
0641..0647
0649..064A
066E..066F
0678..0687
069A..06BF
06C1..06C2
06CC
06CE
06D0..06D1
06FA..06FC
06FF
0712..0714
071A..071D
071F..0727
0729
072B
072D..072E
074E..0758
075C..076A
076D..0770
0772
0775..0777
077A..077F
07CA..07EA
0841..0845
0848
084A..0853
0855
08A0..08A9
08AF..08B0
08B3..08B4
08B6..08B8
08BA..08BD
1807
1820..1842
1843
1844..1877
1887..18A8
18AA
A840..A871
10AC0..10AC4
10AD3..10AD6
10AD8..10ADC
10ADE..10AE0
10AEB..10AEE
10B80
10B82
10B86..10B88
10B8A..10B8B
10B8D
10B90
10BAD..10BAE
1E900..1E943
''')

# http://www.unicode.org/Public/9.0.0/ucd/extracted/DerivedJoiningType.txt
# Joining_Type=Right_Joining
_JOINTYPE_RIGHT_JOINING = CodepointSet('''
0622..0625
0627
0629
062F..0632
0648
0671..0673
0675..0677
0688..0699
06C0
06C3..06CB
06CD
06CF
06D2..06D3
06D5
06EE..06EF
0710
0715..0719
071E
0728
072A
072C
072F
074D
0759..075B
076B..076C
0771
0773..0774
0778..0779
0840
0846..0847
0849
0854
08AA..08AC
08AE
08B1..08B2
08B9
10AC5
10AC7
10AC9..10ACA
10ACE..10AD2
10ADD
10AE1
10AE4
10AEF
10B81
10B83..10B85
10B89
10B8C
10B8E..10B8F
10B91
10BA9..10BAC
''')

# http://www.unicode.org/Public/9.0.0/ucd/extracted/DerivedJoiningType.txt
# Joining_Type=Left_Joining
_JOINTYPE_LEFT_JOINING = CodepointSet('''
A872
10ACD
10AD7
''')

# http://www.unicode.org/Public/9.0.0/ucd/extracted/DerivedJoiningType.txt
# Joining_Type=Transparent
_JOINTYPE_TRANSPARENT = CodepointSet('''
00AD
0300..036F
0483..0487
0488..0489
0591..05BD
05BF
05C1..05C2
05C4..05C5
05C7
0610..061A
061C
064B..065F
0670
06D6..06DC
06DF..06E4
06E7..06E8
06EA..06ED
070F
0711
0730..074A
07A6..07B0
07EB..07F3
0816..0819
081B..0823
0825..0827
0829..082D
0859..085B
08D4..08E1
08E3..0902
093A
093C
0941..0948
094D
0951..0957
0962..0963
0981
09BC
09C1..09C4
09CD
09E2..09E3
0A01..0A02
0A3C
0A41..0A42
0A47..0A48
0A4B..0A4D
0A51
0A70..0A71
0A75
0A81..0A82
0ABC
0AC1..0AC5
0AC7..0AC8
0ACD
0AE2..0AE3
0B01
0B3C
0B3F
0B41..0B44
0B4D
0B56
0B62..0B63
0B82
0BC0
0BCD
0C00
0C3E..0C40
0C46..0C48
0C4A..0C4D
0C55..0C56
0C62..0C63
0C81
0CBC
0CBF
0CC6
0CCC..0CCD
0CE2..0CE3
0D01
0D41..0D44
0D4D
0D62..0D63
0DCA
0DD2..0DD4
0DD6
0E31
0E34..0E3A
0E47..0E4E
0EB1
0EB4..0EB9
0EBB..0EBC
0EC8..0ECD
0F18..0F19
0F35
0F37
0F39
0F71..0F7E
0F80..0F84
0F86..0F87
0F8D..0F97
0F99..0FBC
0FC6
102D..1030
1032..1037
1039..103A
103D..103E
1058..1059
105E..1060
1071..1074
1082
1085..1086
108D
109D
135D..135F
1712..1714
1732..1734
1752..1753
1772..1773
17B4..17B5
17B7..17BD
17C6
17C9..17D3
17DD
180B..180D
1885..1886
18A9
1920..1922
1927..1928
1932
1939..193B
1A17..1A18
1A1B
1A56
1A58..1A5E
1A60
1A62
1A65..1A6C
1A73..1A7C
1A7F
1AB0..1ABD
1ABE
1B00..1B03
1B34
1B36..1B3A
1B3C
1B42
1B6B..1B73
1B80..1B81
1BA2..1BA5
1BA8..1BA9
1BAB..1BAD
1BE6
1BE8..1BE9
1BED
1BEF..1BF1
1C2C..1C33
1C36..1C37
1CD0..1CD2
1CD4..1CE0
1CE2..1CE8
1CED
1CF4
1CF8..1CF9
1DC0..1DF5
1DFB..1DFF
200B
200E..200F
202A..202E
2060..2064
206A..206F
20D0..20DC
20DD..20E0
20E1
20E2..20E4
20E5..20F0
2CEF..2CF1
2D7F
2DE0..2DFF
302A..302D
3099..309A
A66F
A670..A672
A674..A67D
A69E..A69F
A6F0..A6F1
A802
A806
A80B
A825..A826
A8C4..A8C5
A8E0..A8F1
A926..A92D
A947..A951
A980..A982
A9B3
A9B6..A9B9
A9BC
A9E5
AA29..AA2E
AA31..AA32
AA35..AA36
AA43
AA4C
AA7C
AAB0
AAB2..AAB4
AAB7..AAB8
AABE..AABF
AAC1
AAEC..AAED
AAF6
ABE5
ABE8
ABED
FB1E
FE00..FE0F
FE20..FE2F
FEFF
FFF9..FFFB
101FD
102E0
10376..1037A
10A01..10A03
10A05..10A06
10A0C..10A0F
10A38..10A3A
10A3F
10AE5..10AE6
11001
11038..11046
1107F..11081
110B3..110B6
110B9..110BA
110BD
11100..11102
11127..1112B
1112D..11134
11173
11180..11181
111B6..111BE
111CA..111CC
1122F..11231
11234
11236..11237
1123E
112DF
112E3..112EA
11300..11301
1133C
11340
11366..1136C
11370..11374
11438..1143F
11442..11444
11446
114B3..114B8
114BA
114BF..114C0
114C2..114C3
115B2..115B5
115BC..115BD
115BF..115C0
115DC..115DD
11633..1163A
1163D
1163F..11640
116AB
116AD
116B0..116B5
116B7
1171D..1171F
11722..11725
11727..1172B
11C30..11C36
11C38..11C3D
11C3F
11C92..11CA7
11CAA..11CB0
11CB2..11CB3
11CB5..11CB6
16AF0..16AF4
16B30..16B36
16F8F..16F92
1BC9D..1BC9E
1BCA0..1BCA3
1D167..1D169
1D173..1D17A
1D17B..1D182
1D185..1D18B
1D1AA..1D1AD
1D242..1D244
1DA00..1DA36
1DA3B..1DA6C
1DA75
1DA84
1DA9B..1DA9F
1DAA1..1DAAF
1E000..1E006
1E008..1E018
1E01B..1E021
1E023..1E024
1E026..1E02A
1E8D0..1E8D6
1E944..1E94A
E0001
E0020..E007F
E0100..E01EF
''')

# http://www.unicode.org/Public/9.0.0/ucd/Scripts.txt
# Greek
_GREEK_SCRIPT = CodepointSet('''
0370..0373
0375
0376..0377
037A
037B..037D
037F
0384
0386
0388..038A
038C
038E..03A1
03A3..03E1
03F0..03F5
03F6
03F7..03FF
1D26..1D2A
1D5D..1D61
1D66..1D6A
1DBF
1F00..1F15
1F18..1F1D
1F20..1F45
1F48..1F4D
1F50..1F57
1F59
1F5B
1F5D
1F5F..1F7D
1F80..1FB4
1FB6..1FBC
1FBD
1FBE
1FBF..1FC1
1FC2..1FC4
1FC6..1FCC
1FCD..1FCF
1FD0..1FD3
1FD6..1FDB
1FDD..1FDF
1FE0..1FEC
1FED..1FEF
1FF2..1FF4
1FF6..1FFC
1FFD..1FFE
2126
AB65
10140..10174
10175..10178
10179..10189
1018A..1018B
1018C..1018E
101A0
1D200..1D241
1D242..1D244
1D245
''')

# http://www.unicode.org/Public/9.0.0/ucd/Scripts.txt
# Hebrew
_HEBREW_SCRIPT = CodepointSet('''
0591..05BD
05BE
05BF
05C0
05C1..05C2
05C3
05C4..05C5
05C6
05C7
05D0..05EA
05F0..05F2
05F3..05F4
FB1D
FB1E
FB1F..FB28
FB29
FB2A..FB36
FB38..FB3C
FB3E
FB40..FB41
FB43..FB44
FB46..FB4F
''')

# http://www.unicode.org/Public/9.0.0/ucd/Scripts.txt
# Hiragana, Katakana, Han
_HIRAGANA_KATAKANA_HAN = CodepointSet('''
# Hiragana
3041..3096
309D..309E
309F
1B001
1F200
# Katakana
30A1..30FA
30FD..30FE
30FF
31F0..31FF
32D0..32FE
3300..3357
FF66..FF6F
FF71..FF9D
1B000
# Han
2E80..2E99
2E9B..2EF3
2F00..2FD5
3005
3007
3021..3029
3038..303A
303B
3400..4DB5
4E00..9FD5
F900..FA6D
FA70..FAD9
20000..2A6D6
2A700..2B734
2B740..2B81D
2B820..2CEA1
2F800..2FA1D
''')

# http://www.unicode.org/Public/9.0.0/ucd/HangulSyllableType.txt
# Leading_Jamo, Vowel_Jamo, Trailing_Jamo
_OLD_HANGUL_JAMO = CodepointSet('''
# Leading_Jamo
1100..115F
A960..A97C
# Vowel_Jamo
1160..11A7
D7B0..D7C6
# Trailing_Jamo
11A8..11FF
D7CB..D7FB
''')
