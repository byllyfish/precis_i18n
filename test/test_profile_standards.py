"""Independent admission, enforcement, and comparison witnesses."""

import unittest

import precis_i18n.codec  # noqa: F401
from precis_i18n import get_profile
from precis_i18n.baseclass import FreeFormClass
from precis_i18n.profile import Profile, Username
from precis_i18n.unicode import UnicodeData

_USERNAME_PROFILES = (
    "UsernameCasePreserved",
    "UsernameCaseMapped",
    "UsernameCaseMapped:ToLower",
    "UsernameCaseMapped:CaseFold",
)
_NICKNAME_PROFILES = (
    "Nickname",
    "NicknameCasePreserved",
    "NicknameCaseMapped",
    "NicknameCaseMapped:ToLower",
    "NicknameCaseMapped:CaseFold",
)


class UsernameStandardsTest(unittest.TestCase):
    def test_admit_width_mapped_input_before_case_and_nfc(self):
        # RFC 8265 sections 3.3.2 and 3.4.2 require IdentifierClass admission
        # immediately after width mapping.
        for name in _USERNAME_PROFILES:
            profile = get_profile(name)
            for raw, reason in (
                ("\u212aevin", "has_compat"),
                ("L\xb7L", "middle_dot"),
                ("\u2163", "has_compat"),
                ("\u1100\u1161", "old_hangul_jamo"),
                ("\u0378", "unassigned"),
                ("a\u200cb", "zero_width_nonjoiner"),
                ("a\u200db", "zero_width_joiner"),
            ):
                with self.subTest(profile=name, raw=raw):
                    with self.assertRaises(UnicodeEncodeError) as result:
                        profile.enforce(raw)
                    self.assertEqual(result.exception.reason, "DISALLOWED/" + reason)
            with self.subTest(profile=name):
                self.assertEqual(profile.enforce("l\xb7l"), "l\xb7l")
                self.assertEqual(profile.enforce("\uff76\uff9e"), "\u30ac")

    def test_width_mapping_preserves_profile_case_and_precedes_bidi(self):
        self.assertEqual(get_profile("UsernameCasePreserved").enforce("\uff2b"), "K")
        self.assertEqual(get_profile("UsernameCaseMapped").enforce("\uff2b"), "k")
        with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/bidi_rule"):
            get_profile("UsernameCaseMapped").enforce("\u05d0a")

    def test_context_rejection_preserves_unicode_error_contract(self):
        name = "UsernameCaseMapped"
        raw = "L\xb7L"
        with self.assertRaises(UnicodeEncodeError) as result:
            get_profile(name).enforce(raw)
        error = result.exception
        self.assertEqual((error.encoding, error.object), (name, raw))
        self.assertEqual((error.start, error.end, error.reason), (1, 2, "DISALLOWED/middle_dot"))

    def test_profile_comparison_keys_preserve_the_selected_case_policy(self):
        no_casing = get_profile("UsernameCasePreserved")
        lowercase = get_profile("UsernameCaseMapped")
        explicit_lowercase = get_profile("UsernameCaseMapped:ToLower")
        casefold = get_profile("UsernameCaseMapped:CaseFold")
        self.assertEqual(no_casing.comparison_key("E\u0301"), b"\xc3\x89")
        self.assertNotEqual(no_casing.comparison_key("E\u0301"), no_casing.comparison_key("é"))
        self.assertEqual(lowercase.comparison_key("E\u0301"), b"\xc3\xa9")
        self.assertEqual(lowercase.comparison_key("é"), lowercase.comparison_key("É"))
        self.assertEqual(lowercase.comparison_key("Straße"), b"stra\xc3\x9fe")
        self.assertNotEqual(lowercase.comparison_key("Straße"), lowercase.comparison_key("STRASSE"))
        self.assertEqual(explicit_lowercase.comparison_key("Straße"), lowercase.comparison_key("Straße"))
        self.assertEqual(casefold.comparison_key("Straße"), casefold.comparison_key("STRASSE"))
        self.assertEqual(lowercase.comparison_key("AΣ"), "aς".encode())
        self.assertEqual(lowercase.comparison_key("AΣA"), "aσa".encode())
        self.assertEqual(lowercase.comparison_key("İ"), "i\u0307".encode())
        self.assertEqual(lowercase.comparison_key("Iı"), "iı".encode())
        self.assertEqual(lowercase.comparison_key("\U00010400"), "\U00010428".encode())

    def test_reassigning_public_class_adapter_changes_casing_with_other_operations(self):
        class AlternateUnicodeData(UnicodeData):
            def lower(self, value):
                return value.replace("A", "b").lower()

        profile = get_profile("UsernameCaseMapped")
        self.assertEqual(profile.enforce("A"), "a")
        profile.base.ucd = AlternateUnicodeData()
        self.assertEqual(profile.enforce("A"), "b")


class FreeformStandardsTest(unittest.TestCase):
    def test_opaque_string_uses_nfc_and_preserves_case_width_and_directionality(self):
        # RFC 8265 section 4.2.2 maps spaces without trimming or folding.
        profile = get_profile("OpaqueString")
        self.assertEqual(profile.comparison_key("\uff21\u2000E\u0301\u05d0"), "Ａ Éא".encode())
        self.assertNotEqual(profile.comparison_key("Ａ A"), profile.comparison_key("A A"))
        self.assertNotEqual(profile.comparison_key("A"), profile.comparison_key("a"))
        self.assertEqual(profile.comparison_key(" \u00a0 "), b"   ")
        for raw, reason in (
            ("", "empty"),
            ("\x00", "controls"),
            ("L\xb7L", "middle_dot"),
            ("\u1100\u1161", "old_hangul_jamo"),
            ("\u0378", "unassigned"),
            ("\ud800", "other"),
            ("\ue000", "other"),
        ):
            with self.subTest(raw=raw), self.assertRaisesRegex(UnicodeEncodeError, reason):
                profile.comparison_key(raw)
        with self.assertRaises(UnicodeDecodeError):
            profile.comparison_key(b"\xff")
        self.assertEqual(profile.comparison_key(b"abc"), b"abc")

    def test_nickname_case_preserved_enforces_display_and_compares_with_lowercase(self):
        # RFC 8266 sections 2.1, 2.3, and 2.4 distinguish display and comparison.
        profile = get_profile("NicknameCasePreserved")
        self.assertEqual(profile.enforce("\u2003Richard  \u2163 "), "Richard IV")
        self.assertEqual(profile.comparison_key("\u2003Richard  \u2163 "), b"richard iv")
        self.assertEqual(profile.enforce("\u03d4"), "\u03ab")
        self.assertEqual(profile.comparison_key("\u03d4"), "\u03cb".encode())
        self.assertEqual(profile.comparison_key("Σ"), profile.comparison_key("σ"))
        self.assertNotEqual(profile.comparison_key("Σ"), profile.comparison_key("ς"))
        self.assertEqual(profile.enforce("abc\u05d0"), "abc\u05d0")
        # The codec follows display enforcement.
        self.assertEqual("  Richard \u2163".encode("NicknameCasePreserved"), b"Richard IV")

    def test_legacy_nickname_aliases_preserve_their_mapping(self):
        for name in ("Nickname", "NicknameCaseMapped", "NicknameCaseMapped:ToLower"):
            with self.subTest(profile=name):
                profile = get_profile(name)
                self.assertEqual(profile.enforce("Straße"), "straße")
                self.assertEqual(profile.comparison_key("Straße"), "straße".encode())
                self.assertEqual("Straße".encode(name), "straße".encode())
        profile = get_profile("NicknameCaseMapped:CaseFold")
        self.assertEqual(profile.enforce("Straße"), "strasse")
        self.assertEqual(profile.comparison_key("Straße"), b"strasse")
        self.assertEqual("Straße".encode("NicknameCaseMapped:CaseFold"), b"strasse")

    def test_nickname_prepares_the_class_before_mapping(self):
        for name in _NICKNAME_PROFILES:
            profile = get_profile(name)
            with self.subTest(profile=name):
                with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/middle_dot"):
                    profile.enforce("L\xb7L")
                with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/empty"):
                    profile.enforce("\u00a0\u2000")
                with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/old_hangul_jamo"):
                    profile.enforce("\u1100\u1161")
                self.assertEqual(profile.enforce("l\xb7l"), "l\xb7l")

    def test_unprofiled_classes_and_codecs_do_not_apply_profile_mapping(self):
        for name, value in (
            ("IdentifierClass", "E\u0301"),
            ("FreeFormClass", "\uff21\u2000E\u0301\u05d0"),
        ):
            with self.subTest(profile=name):
                self.assertEqual(get_profile(name).enforce(value), value)
                self.assertEqual(value.encode(name), value.encode("utf-8"))
        with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/has_compat"):
            get_profile("IdentifierClass").enforce("\u212a")
        self.assertEqual(get_profile("FreeFormClass").enforce("\u212a"), "\u212a")


class StabilizationTest(unittest.TestCase):
    @staticmethod
    def observe_admission(profile):
        observed = []
        enforce = profile.base.enforce

        def admit(value, name):
            observed.append(value)
            return enforce(value, name)

        profile.base.enforce = admit
        return observed

    def test_unchanged_profiles_admit_once_per_call(self):
        for name in ("UsernameCaseMapped", "OpaqueString", "NicknameCasePreserved"):
            with self.subTest(profile=name):
                profile = get_profile(name)
                observed = self.observe_admission(profile)
                self.assertEqual(profile.comparison_key("example"), b"example")
                self.assertEqual(profile.comparison_key("example"), b"example")
                self.assertEqual(observed, ["example", "example"])

    def test_changed_profiles_admit_each_distinct_stage(self):
        for name, raw, admitted, expected in (
            ("OpaqueString", "cafe\u0301", "cafe\u0301", "caf\u00e9"),
            ("UsernameCaseMapped", "\uff21bc", "Abc", "abc"),
        ):
            with self.subTest(profile=name):
                profile = get_profile(name)
                observed = self.observe_admission(profile)
                self.assertEqual(profile.enforce(raw), expected)
                self.assertEqual(observed, [admitted, expected])

    def test_rejects_an_invalid_raw_context_and_newly_invalid_output_context(self):
        profile = get_profile("UsernameCaseMapped")
        observed = self.observe_admission(profile)
        with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/middle_dot"):
            profile.enforce("L\xb7L")
        self.assertEqual(observed, ["L\xb7L"])

        profile = get_profile("NicknameCasePreserved")
        observed = self.observe_admission(profile)
        # U+037A has the Greek script, but NFKC replaces it with
        # a space and a combining mark. The resulting context is invalid.
        with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/greek_keraia"):
            profile.enforce("\u0375\u037a")
        self.assertEqual(observed, ["\u0375\u037a", "\u0375 \u0345"])

    def test_unchanged_subclass_still_calls_overridden_hooks(self):
        observed = []

        class CustomUsername(Username):
            def apply_five_rules(self, value):
                observed.append("rules")
                return super().apply_five_rules(value)

            def idempotence_check(self, value):
                observed.append("idempotence")
                return super().idempotence_check(value)

        profile = CustomUsername(UnicodeData(), "CustomUsername")
        self.assertEqual(profile.enforce("example"), "example")
        self.assertEqual(observed, ["rules", "idempotence", "rules"])

    def test_supports_three_additional_passes_for_stability(self):
        class ConvergingProfile(Profile):
            def additional_mapping_rule(self, value):
                return {"w": "x", "x": "y", "y": "z"}.get(value, value)

        profile = ConvergingProfile(FreeFormClass(UnicodeData()), "ConvergingProfile")
        self.assertEqual(profile.enforce("w"), "z")
        self.assertEqual(profile.enforce("z"), "z")

    def test_rejects_after_four_total_nonstabilizing_passes(self):
        calls = []

        class DivergingProfile(Profile):
            def additional_mapping_rule(self, value):
                calls.append(value)
                return value + "x"

        profile = DivergingProfile(FreeFormClass(UnicodeData()), "DivergingProfile")
        with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/not_idempotent"):
            profile.enforce("w")
        self.assertEqual(calls, ["w", "wx", "wxx", "wxxx"])


if __name__ == "__main__":
    unittest.main()
