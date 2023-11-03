import unittest

import precis_i18n
from precis_i18n import get_profile
from precis_i18n.unicode import UnicodeData


class TestGetProfile(unittest.TestCase):
    def test_missing(self):
        with self.assertRaises(KeyError):
            get_profile("_does_not_exist_")

    def test_unicodedata_arg(self):
        import unicodedata

        profile = get_profile("UsernameCasePreserved", unicodedata=unicodedata)
        self.assertEqual(profile.enforce("E\u0301\u0301\u0301"), "\u00c9\u0301\u0301")


class TestUsernameCasePreserved(unittest.TestCase):
    def test_enforce(self):
        profile = get_profile("UsernameCasePreserved")
        self.assertEqual(profile.enforce("Juliet"), "Juliet")
        self.assertEqual(profile.enforce("J*"), "J*")
        self.assertEqual(profile.enforce("E\u0301\u0301\u0301"), "\u00c9\u0301\u0301")
        self.assertEqual(profile.enforce(b"Juliet"), "Juliet")

        self.profile_fail(profile, "", "empty")
        self.profile_fail(profile, " J", "spaces")
        self.profile_fail(profile, "\u05d0*", "bidi_rule")

    def profile_fail(self, profile, value, reason):
        with self.assertRaisesRegex(UnicodeEncodeError, reason):
            profile.enforce(value)

    def test_invalid_argument(self):
        profile = get_profile("UsernameCasePreserved")
        with self.assertRaisesRegex(ValueError, "not a string"):
            profile.enforce(1)

    def test_identifier_oddities(self):
        # Make a list of all codepoints < 10,000 which are allowed in the
        # UsernameCasePreserved profile even though they are not allowed in
        # IdentifierClass.
        profile = get_profile("UsernameCasePreserved")
        allowed = []
        for cp in range(0, 10000):
            try:
                profile.enforce(chr(cp))
                try:
                    profile.base.enforce(chr(cp))
                except UnicodeEncodeError:
                    allowed.append(cp)
            except UnicodeEncodeError:
                pass
        self.assertEqual(
            allowed,
            [
                832,
                833,
                835,
                836,
                884,
                894,
                2392,
                2393,
                2394,
                2395,
                2396,
                2397,
                2398,
                2399,
                2524,
                2525,
                2527,
                2611,
                2614,
                2649,
                2650,
                2651,
                2654,
                2908,
                2909,
                3907,
                3917,
                3922,
                3927,
                3932,
                3945,
                3955,
                3957,
                3958,
                3960,
                3969,
                3987,
                3997,
                4002,
                4007,
                4012,
                4025,
                8049,
                8051,
                8053,
                8055,
                8057,
                8059,
                8061,
                8123,
                8126,
                8137,
                8139,
                8147,
                8155,
                8163,
                8171,
                8175,
                8185,
                8187,
                8486,
                8490,
                8491,
            ],
        )


class TestUsernameCaseMapped(unittest.TestCase):
    def test_enforce(self):
        profile = get_profile("UsernameCaseMapped")
        self.assertEqual(profile.enforce("Juliet"), "juliet")
        self.assertEqual(profile.enforce("E\u0301\u0301\u0301"), "\u00e9\u0301\u0301")


class TestNickname(unittest.TestCase):
    def test_enforce(self):
        profile = get_profile("Nickname")
        self.assertEqual(profile.enforce("Juliet"), "juliet")
        self.assertEqual(profile.enforce("E\u0301\u0301\u0301"), "\u00e9\u0301\u0301")
        self.assertEqual(profile.enforce("\u03d4"), "\u03cb")


class TestNicknameCaseMapped(unittest.TestCase):
    def test_enforce(self):
        profile = get_profile("NicknameCaseMapped:ToLower")
        self.assertEqual(profile.enforce("Juliet"), "juliet")
        self.assertEqual(profile.enforce("E\u0301\u0301\u0301"), "\u00e9\u0301\u0301")
        self.assertEqual(profile.enforce("\u03d4"), "\u03cb")


class TestUsername(unittest.TestCase):
    def test_constructor(self):
        profile = precis_i18n.profile.Username(UnicodeData(), "name", "lower")
        self.assertEqual(profile.enforce("Fu\u00dfball"), "fu\u00dfball")

    def test_constructor_fail(self):
        with self.assertRaises(ValueError):
            precis_i18n.profile.Username(UnicodeData(), "name", "unsupported-arg")
