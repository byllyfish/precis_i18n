# test_precis.py

import platform
import sys
import unittest

import precis_i18n.context as pc
from precis_i18n.baseclass import FreeFormClass, IdentifierClass
from precis_i18n.bidi import bidi_rule, has_rtl
from precis_i18n.derived import derived_property
from precis_i18n.unicode import UnicodeData, _version_to_float

_PYPY = platform.python_implementation() == "PyPy"
_PY3_11 = sys.version_info[:2] >= (3, 11)

UCD = UnicodeData()

# Example characters for bidirectional properties. Used in testing Bidi Rule.
L = "A"
R = "\u05d0"
AL = "\u0621"
EN = "0"
AN = "\U00010e60"
NSM = "\u0300"
P = "*"


class TestBidiRule(unittest.TestCase):
    def test_bidi_rule_ltr(self):
        self.assertTrue(bidi_rule(L, UCD))
        self.assertTrue(bidi_rule(L + P + L, UCD))
        self.assertFalse(bidi_rule(P + L, UCD))
        self.assertFalse(bidi_rule(L + P, UCD))
        self.assertFalse(bidi_rule(L + R + L, UCD))

    def test_bidi_rule_rtl(self):
        self.assertTrue(bidi_rule(R, UCD))
        self.assertTrue(bidi_rule(R + R, UCD))
        self.assertTrue(bidi_rule(AL + R, UCD))
        self.assertTrue(bidi_rule(AL + EN + R, UCD))
        self.assertTrue(bidi_rule(AL + R + EN, UCD))
        self.assertTrue(bidi_rule(R + P + R, UCD))
        self.assertTrue(bidi_rule(R + P + R + NSM + NSM, UCD))
        self.assertTrue(bidi_rule(R + AN + NSM + AN + R, UCD))
        self.assertFalse(bidi_rule(P + R, UCD))
        self.assertFalse(bidi_rule(R + P, UCD))
        self.assertFalse(bidi_rule(R + L + R, UCD))
        self.assertFalse(bidi_rule(EN + R, UCD))
        self.assertFalse(bidi_rule(R + AN + EN, UCD))
        self.assertFalse(bidi_rule(R + EN + AN + R, UCD))

    def test_has_rtl(self):
        self.assertFalse(has_rtl("Juliet+", UCD))
        self.assertTrue(has_rtl("\u05d0+", UCD))


class TestPrecisIdentifierClass(unittest.TestCase):
    def test_valid_identifier(self):
        ident = IdentifierClass(UCD)
        self.assertEqual(ident.name, "IdentifierClass")
        self.assertEqual(ident.enforce("abc"), "abc")
        self.assertEqual(ident.enforce("123"), "123")
        self.assertEqual(
            ident.enforce("\u0660\u0661\u0662\u0669"), "\u0660\u0661\u0662\u0669"
        )
        self.assertEqual(ident.enforce("\u0370\u0371"), "\u0370\u0371")
        # CONTEXTJ
        self.assertEqual(ident.enforce("\u094d\u200c"), "\u094d\u200c")

    def test_invalid_identifier(self):
        ident = IdentifierClass(UCD)
        # DISALLOWED/spaces
        with self.assertRaisesRegex(
            UnicodeEncodeError,
            r"'IdentifierClass' codec can't encode character '\\x20' in position 0: DISALLOWED/spaces",
        ):
            ident.enforce(" ")

        # DISALLOWED/precis_ignorable_properties
        with self.assertRaisesRegex(
            UnicodeEncodeError,
            r"'IdentifierClass' codec can't encode character '\\xad' in position 0: DISALLOWED/precis_ignorable_properties",
        ):
            ident.enforce("\xad")

        # DISALLOWED/old_hangul_jamo
        with self.assertRaisesRegex(
            UnicodeEncodeError,
            r"'IdentifierClass' codec can't encode character '\\u1100' in position 0: DISALLOWED/old_hangul_jamo",
        ):
            ident.enforce("\u1100")

        # DISALLOWED/has_compat
        with self.assertRaisesRegex(
            UnicodeEncodeError,
            r"'IdentifierClass' codec can't encode character '\\u1fbf' in position 0: DISALLOWED/has_compat",
        ):
            ident.enforce("\u1FBF")


class TestPrecisFreeformClass(unittest.TestCase):
    def test_valid_freeform(self):
        free = FreeFormClass(UCD)
        self.assertEqual(free.name, "FreeFormClass")

        self.assertEqual(free.enforce("abc"), "abc")
        self.assertEqual(free.enforce("123"), "123")
        self.assertEqual(
            free.enforce("\u0660\u0661\u0662\u0669"), "\u0660\u0661\u0662\u0669"
        )
        self.assertEqual(free.enforce("\u0370\u0371"), "\u0370\u0371")
        self.assertEqual(free.enforce(" "), " ")
        self.assertEqual(free.enforce("\u1FBF"), "\u1FBF")

    def test_invalid_freeform(self):
        free = FreeFormClass(UCD)

        # DISALLOWED/precis_ignorable_properties
        with self.assertRaisesRegex(
            UnicodeEncodeError,
            r"'FreeFormClass' codec can't encode character '\\xad' in position 0: DISALLOWED/precis_ignorable_properties",
        ):
            free.enforce("\xad")

        # DISALLOWED/old_hangul_jamo
        with self.assertRaisesRegex(
            UnicodeEncodeError,
            r"'FreeFormClass' codec can't encode character '\\u1100' in position 0: DISALLOWED/old_hangul_jamo",
        ):
            free.enforce("\u1100")

        # DISALLOWED/other (surrogates)
        with self.assertRaisesRegex(
            UnicodeEncodeError,
            r"'FreeFormClass' codec can't encode character '\\ud800' in position 0: DISALLOWED/other",
        ):
            if _PYPY:
                # pypy3-v5.5.0 treats surrogate pairs in .pyc files differently. (issue #2441)
                free.enforce("\ud800 \udc00")
            else:
                free.enforce("\ud800\udc00")


class TestDerivedProperty(unittest.TestCase):
    def test_derived_property(self):
        self.assertEqual(derived_property(0, UCD), ("DISALLOWED", "controls"))
        self.assertEqual(
            derived_property(0x10FFFF, UCD),
            ("DISALLOWED", "precis_ignorable_properties"),
        )
        self.assertEqual(derived_property(0x30, UCD), ("PVALID", "ascii7"))
        self.assertEqual(derived_property(0x20, UCD), ("FREE_PVAL", "spaces"))
        self.assertEqual(
            derived_property(0xAD, UCD), ("DISALLOWED", "precis_ignorable_properties")
        )

        with self.assertRaises(ValueError):
            derived_property(0x110000, UCD)

        # In Unicode 9.0, U+08E2 is 'DISALLOWED'. Before Unicode 9.0, it is
        # UNASSIGNED.
        prop = derived_property(0x08E2, UCD)[0]
        if UCD.version >= 9.0:
            self.assertEqual(prop, "DISALLOWED")
        else:
            self.assertEqual(prop, "UNASSIGNED")


class TestPrecisContextRule(unittest.TestCase):
    def test_rule_zero_width_nonjoiner(self):
        # We're going to use a872 and 0622 in some tests. Make sure they aren't
        # combining_virama().
        self.assertFalse(UCD.combining_virama(0xA872))
        self.assertFalse(UCD.combining_virama(0x0622))
        # Valid: combining_virama before
        self.assertTrue(pc.rule_zero_width_nonjoiner("\u094d\u200c", 1, UCD))
        # Invalid: invalid join_type
        self.assertFalse(pc.rule_zero_width_nonjoiner("\ua872\u200c", 1, UCD))
        # Invalid: undefined before
        with self.assertRaises(IndexError):
            pc.rule_zero_width_nonjoiner("\u200c", 0, UCD)
        # Valid: jointype(L J R)
        self.assertTrue(pc.rule_zero_width_nonjoiner("\ua872\u200c\u0622", 1, UCD))
        # Invalid: jointype(R J L)
        self.assertFalse(pc.rule_zero_width_nonjoiner("\u0622\u200c\ua872", 1, UCD))

    def test_rule_zero_width_joiner(self):
        # Valid: combining_virama before
        self.assertTrue(pc.rule_zero_width_joiner("\u094d\u200d", 1, UCD))
        # Invalid: no combining_virama before
        self.assertFalse(pc.rule_zero_width_joiner("A\u200d", 1, UCD))
        # Invalid: no combining_virama before, jointype(L J R)
        self.assertFalse(pc.rule_zero_width_joiner("\ua872\u200d\u0622", 1, UCD))

    def test_rule_middle_dot(self):
        # Valid: 6c b7 6c
        self.assertTrue(pc.rule_middle_dot("\u006c\u00b7\u006c", 1, UCD))
        # Invalid before: 6d b7 6c
        self.assertFalse(pc.rule_middle_dot("\u006d\u00b7\u006c", 1, UCD))
        # Invalid after: 6c b7 6d
        self.assertFalse(pc.rule_middle_dot("\u006c\u00b7\u006d", 1, UCD))
        # Invalid: undefined before
        with self.assertRaises(IndexError):
            pc.rule_middle_dot("\u00b7\u006c", 0, UCD)
        # Invalid: undefined after
        with self.assertRaises(IndexError):
            pc.rule_middle_dot("\u006c\u00b7", 1, UCD)

    def test_rule_greek_keraia(self):
        # Valid: 0375 03ff
        self.assertTrue(pc.rule_greek_keraia("\u0375\u03ff", 0, UCD))
        # Invalid: 0375 1d25
        self.assertFalse(pc.rule_greek_keraia("\u0375\u1d25", 0, UCD))
        # Invalid: undefined after
        with self.assertRaises(IndexError):
            pc.rule_greek_keraia("\u0375", 0, UCD)

    def test_rule_hebrew_punctuation(self):
        # Valid: 0591 05f3
        self.assertTrue(pc.rule_hebrew_punctuation("\u0591\u05f3", 1, UCD))
        # Valid: 0591 05f4
        self.assertTrue(pc.rule_hebrew_punctuation("\u0591\u05f4", 1, UCD))
        # Invalid: 0031 05f3
        self.assertFalse(pc.rule_hebrew_punctuation("\u0031\u05f3", 1, UCD))
        # Invalid: 0031 05f4
        self.assertFalse(pc.rule_hebrew_punctuation("\u0031\u05f4", 1, UCD))
        # Invalid: undefined after
        with self.assertRaises(IndexError):
            pc.rule_hebrew_punctuation("\u05f3", 0, UCD)

    def test_katatana_middle_dot(self):
        # Valid: 0x30fb 0x2e99
        self.assertTrue(pc.rule_katakana_middle_dot("\u30fb\u2e99", 0, UCD))
        # Valid: 0x30f0 0x30fb 0x0021
        self.assertTrue(pc.rule_katakana_middle_dot("\u30f0\u30fb\u0021", 1, UCD))
        # Invalid: 0x30fb 0x3006
        self.assertFalse(pc.rule_katakana_middle_dot("\u30fb\u3006", 0, UCD))
        # Invalid: 0x30fb 0x0021
        self.assertFalse(pc.rule_katakana_middle_dot("\u0021\u30fb", 1, UCD))
        # Invalid: 0x30fb
        self.assertFalse(pc.rule_katakana_middle_dot("\u30fb", 0, UCD))

    def test_arabic_indic(self):
        # Valid: 0x0660 0x0661 0x0662 0x0669
        self.assertTrue(pc.rule_arabic_indic("\u0660\u0661\u0662\u0669", 0, UCD))
        # Invalid: 0x660 0x0661 0x0662 0x06f0
        self.assertFalse(pc.rule_arabic_indic("\u0660\u0661\u0662\u06f0", 0, UCD))

    def test_extended_arabic_indic(self):
        # Valid: 0x06f0 0x06f1 0x06f2 0x06f9
        self.assertTrue(
            pc.rule_extended_arabic_indic("\u06f0\u06f1\u06f2\u06f9", 0, UCD)
        )
        # Invalid: 0x6f0 0x06f1 0x06f2 0x0660
        self.assertFalse(
            pc.rule_extended_arabic_indic("\u06f0\u06f1\u06f2\u0660", 0, UCD)
        )

    def test_context_rule(self):
        def _context_rule(value, offset, ucd):
            return not pc.context_rule_error(value, offset, ucd)

        # 1. rule_zero_width_nonjoiner
        # Valid: combining_virama before
        self.assertTrue(_context_rule("\u094d\u200c", 1, UCD))
        # Invalid: invalid join_type
        self.assertFalse(_context_rule("\ua872\u200c", 1, UCD))
        # Invalid: undefined before
        self.assertFalse(_context_rule("\u200c", 0, UCD))
        # Valid: jointype(L J R)
        self.assertTrue(_context_rule("\ua872\u200c\u0622", 1, UCD))
        # Invalid: jointype(R J L)
        self.assertFalse(_context_rule("\u0622\u200c\ua872", 1, UCD))

        # 2. rule_zero_width_joiner
        # Valid: combining_virama before
        self.assertTrue(_context_rule("\u094d\u200d", 1, UCD))
        # Invalid: no combining_virama before
        self.assertFalse(_context_rule("A\u200d", 1, UCD))
        # Invalid: no combining_virama before, jointype(L J R)
        self.assertFalse(_context_rule("\ua872\u200d\u0622", 1, UCD))

        # 3. rule_middle_dot
        # Valid: 6c b7 6c
        self.assertTrue(_context_rule("\u006c\u00b7\u006c", 1, UCD))
        # Invalid before: 6d b7 6c
        self.assertFalse(_context_rule("\u006d\u00b7\u006c", 1, UCD))
        # Invalid after: 6c b7 6d
        self.assertFalse(_context_rule("\u006c\u00b7\u006d", 1, UCD))
        # Invalid: undefined before
        self.assertFalse(_context_rule("\u00b7\u006c", 0, UCD))
        # Invalid: undefined after
        self.assertFalse(_context_rule("\u006c\u00b7", 1, UCD))

        # 4. rule_greek_keraia
        # Valid: 0375 03ff
        self.assertTrue(_context_rule("\u0375\u03ff", 0, UCD))
        # Invalid: 0375 1d25
        self.assertFalse(_context_rule("\u0375\u1d25", 0, UCD))
        # Invalid: undefined after
        self.assertFalse(_context_rule("\u0375", 0, UCD))

        # 5. rule_hebrew_punctuation
        # Valid: 0591 05f3
        self.assertTrue(_context_rule("\u0591\u05f3", 1, UCD))
        # Valid: 0591 05f4
        self.assertTrue(_context_rule("\u0591\u05f4", 1, UCD))
        # Invalid: 0031 05f3
        self.assertFalse(_context_rule("\u0031\u05f3", 1, UCD))
        # Invalid: 0031 05f4
        self.assertFalse(_context_rule("\u0031\u05f4", 1, UCD))
        # Invalid: undefined after
        self.assertFalse(_context_rule("\u05f3", 0, UCD))
        # Valid: 05EF 05f3 (Unicode >= 11.0)
        self.assertTrue(_context_rule("\u05EF\u05f3", 1, UCD))

        # 6. katakana_middle_dot
        # Valid: 0x30fb 0x2e99
        self.assertTrue(_context_rule("\u30fb\u2e99", 0, UCD))
        # Valid: 0x30f0 0x30fb 0x0021
        self.assertTrue(_context_rule("\u30f0\u30fb\u0021", 1, UCD))
        # Invalid: 0x30fb 0x3006
        self.assertFalse(_context_rule("\u30fb\u3006", 0, UCD))
        # Invalid: 0x30fb 0x0021
        self.assertFalse(_context_rule("\u0021\u30fb", 1, UCD))
        # Invalid: 0x30fb
        self.assertFalse(_context_rule("\u30fb", 0, UCD))
        # Valid: 0x30fb 0x3400 (Unicode >= X)
        self.assertTrue(_context_rule("\u30fb\u3400", 0, UCD))

        # 7. arabic_indic
        # Valid: 0x0660 0x0661 0x0662 0x0669
        self.assertTrue(_context_rule("\u0660\u0661\u0662\u0669", 0, UCD))
        # Invalid: 0x660 0x0661 0x0662 0x06f0
        self.assertFalse(_context_rule("\u0660\u0661\u0662\u06f0", 0, UCD))

        # 8. extended_arabic_indic
        # Valid: 0x06f0 0x06f1 0x06f2 0x06f9
        self.assertTrue(_context_rule("\u06f0\u06f1\u06f2\u06f9", 0, UCD))
        # Invalid: 0x6f0 0x06f1 0x06f2 0x0660
        self.assertFalse(_context_rule("\u06f0\u06f1\u06f2\u0660", 0, UCD))

        # 9. No rule matches.
        with self.assertRaises(KeyError):
            _context_rule("a", 0, UCD)


class TestPrecisUnicodeData(unittest.TestCase):
    def test_width_map(self):
        self.assertEqual(
            UCD.width_map("\uff00\uff01\uff02\uffe3\uffef"), '\uff00!"\uffe3\uffef'
        )

    def test_replace_whitespace(self):
        self.assertEqual(
            UCD.map_nonascii_space_to_ascii(
                " .\u00a0.\u1680 .\u2000.\u200A.\u202F.\u205F.\u3000"
            ),
            " . .  . . . . . ",
        )

    def test_default_ignorable_code_point(self):
        self.assertTrue(UCD.default_ignorable(0x00AD))
        self.assertFalse(UCD.default_ignorable(0x00AE))

    def test_has_compat(self):
        self.assertFalse(UCD.has_compat(0x31))
        self.assertTrue(UCD.has_compat(0xFF01))
        self.assertTrue(UCD.has_compat(0x212B))

    def test_control(self):
        self.assertFalse(UCD.control(0x20))
        self.assertTrue(UCD.control(0x0A))
        self.assertTrue(UCD.control(0x80))

    def test_noncharacter(self):
        self.assertTrue(UCD.noncharacter(0x02FFFF))
        self.assertTrue(UCD.noncharacter(0xFDEF))
        self.assertFalse(UCD.noncharacter(0xFDF0))

    def test_old_hangul_jamo(self):
        self.assertTrue(UCD.old_hangul_jamo(0xA97C))
        self.assertFalse(UCD.old_hangul_jamo(0xA97D))

    def test_greek_script(self):
        self.assertTrue(UCD.greek_script(0x0373))
        self.assertFalse(UCD.greek_script(0x0374))

    def test_hebrew_script(self):
        self.assertTrue(UCD.hebrew_script(0x05C7))
        self.assertFalse(UCD.hebrew_script(0x05C8))

    def test_hiragana_katakana_han_script(self):
        self.assertTrue(UCD.hiragana_katakana_han_script(0x1F200))
        self.assertFalse(UCD.hiragana_katakana_han_script(0x1F201))
        self.assertTrue(UCD.hiragana_katakana_han_script(0xFF9D))
        self.assertFalse(UCD.hiragana_katakana_han_script(0xFF9E))
        self.assertTrue(UCD.hiragana_katakana_han_script(0x2FD5))
        self.assertFalse(UCD.hiragana_katakana_han_script(0x2FD6))
        self.assertFalse(UCD.hiragana_katakana_han_script(0x3006))
        self.assertFalse(UCD.hiragana_katakana_han_script(0x30FB))

    def test_combining_virama(self):
        self.assertTrue(UCD.combining_virama(0x1714))
        if _PY3_11:
            self.assertTrue(UCD.combining_virama(0x1715))
        else:
            self.assertFalse(UCD.combining_virama(0x1715))
        self.assertFalse(UCD.combining_virama(0x1716))

    def test_arabic_indic(self):
        self.assertTrue(UCD.arabic_indic(0x669))
        self.assertFalse(UCD.arabic_indic(0x66A))

    def test_extended_arabic_indic(self):
        self.assertTrue(UCD.extended_arabic_indic(0x06F9))
        self.assertFalse(UCD.extended_arabic_indic(0x06FA))

    def test_valid_join_type(self):
        # Valid: L J R
        self.assertTrue(UCD.valid_jointype("\ua872\u200c\u0622", 1))
        # Valid: L T J T R
        self.assertTrue(UCD.valid_jointype("\ua872\u00ad\u200c\u00ad\u0622", 2))
        # Valid: D J D
        self.assertTrue(UCD.valid_jointype("\u0620\u200c\u0620", 1))
        # Valid: D T J T D
        self.assertTrue(UCD.valid_jointype("\u0626\u0300\u200c\u0301\u0628", 2))

        # Invalid: R J L
        self.assertFalse(UCD.valid_jointype("\u0622\u200c\ua872", 1))
        # Invalid: R T J T L
        self.assertFalse(UCD.valid_jointype("\u0622\u00ad\u200c\u00ad\ua872", 2))
        # Invalid: J
        self.assertFalse(UCD.valid_jointype("\u200c", 0))
        # Invalid: T J T
        self.assertFalse(UCD.valid_jointype("\u00ad\u200c\u00ad", 1))
        # Invalid: U T J T U
        self.assertFalse(UCD.valid_jointype("\u0031\u0300\u200c\u0301\u0032", 2))

        # Valid: L J R   (Unicode >= 14.0)
        self.assertTrue(UCD.valid_jointype("\U00010D00\u200c\u088E", 1))
        # Valid: L T J T R  (Unicode >= 14.0)
        self.assertTrue(UCD.valid_jointype("\U00010D00\u07fd\u200c\u07fd\u088E", 2))
        # Valid: D J D  (Unicode >= 14.0)
        self.assertTrue(UCD.valid_jointype("\u0886\u200c\u0886", 1))

    def test_version_to_float(self):
        self.assertEqual(_version_to_float("8.0.0"), 8.0)
        self.assertEqual(_version_to_float("6.3.1"), 6.3)
        with self.assertRaises(ValueError):
            _version_to_float("8.0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
