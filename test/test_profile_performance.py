"""Deterministic work and compatibility witnesses for profile optimizations."""

from collections import Counter
from itertools import product
import sys
import unittest

from precis_i18n import get_profile
from precis_i18n.unicode import UnicodeData


def observe_calls(operation):
    """Measure calls to real PRECIS functions on one thread."""
    counts = Counter()

    def observe(frame, event, _arg):
        if event == "call" and frame.f_globals.get("__name__", "").startswith("precis_i18n."):
            counts[frame.f_code.co_name] += 1

    original = sys.getprofile()
    sys.setprofile(observe)
    try:
        return operation(), counts
    finally:
        sys.setprofile(original)


class NativeProfileWorkTest(unittest.TestCase):
    def test_native_bidi_rejects_with_the_same_bounds_in_one_direction_scan(self):
        username = get_profile("UsernameCaseMapped")

        def reject():
            with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/bidi_rule") as raised:
                username.enforce("aא")
            error = raised.exception
            return error.object, error.start, error.end

        actual, calls = observe_calls(reject)
        self.assertEqual(actual, ("aא", 0, 2))
        self.assertEqual(calls["_native_username_bidi"], 1)
        self.assertEqual(calls["bidirectional"], 0)

    def test_username_bidi_matches_generic_for_directional_combinations(self):
        class AlternateUnicodeData(UnicodeData):
            pass

        native = get_profile("UsernameCaseMapped")
        generic = get_profile("UsernameCaseMapped")
        generic.base.ucd = AlternateUnicodeData()

        def outcome(profile, value):
            try:
                return profile.directionality_rule(value)
            except UnicodeEncodeError as error:
                return error.object, error.start, error.end, error.reason

        alphabet = ("a", "א", "م", "١", "1", "+", ".", "$", ")", "\u0301",
                    "\u200c", " ", "\n", "\u202a", "\u2067", "\u0378")
        for length in range(4):
            for parts in product(alphabet, repeat=length):
                value = "".join(parts)
                self.assertEqual(outcome(native, value), outcome(generic, value), value)

    def test_ordinary_native_characters_use_the_same_two_admissions(self):
        username = get_profile("UsernameCaseMapped")
        username.enforce("é")
        actual, calls = observe_calls(lambda: username.enforce("Élise-漢字"))
        self.assertEqual(actual, "élise-漢字")
        self.assertEqual(calls["enforce"], 3)
        self.assertEqual(calls["derived_property"], 0)

    def test_width_mapped_ascii_username_uses_proven_ascii_invariants(self):
        username = get_profile("UsernameCaseMapped")
        actual, calls = observe_calls(lambda: username.enforce("Ａ-Ｂ"))
        self.assertEqual(actual, "a-b")
        self.assertEqual(calls["normalization_rule"], 0)
        self.assertEqual(calls["has_rtl"], 0)
        with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/spaces"):
            username.enforce("Ａ\u3000Ｂ")

    def test_ascii_username_preserves_an_instance_normalization_override(self):
        username = get_profile("UsernameCaseMapped")
        username.normalization_rule = lambda value: value.replace("a", "z")
        self.assertEqual(username.enforce("Ａ"), "z")

    def test_common_native_classification_uses_fixed_unicode_data(self):
        username = get_profile("UsernameCaseMapped")
        username.enforce("é")
        actual, calls = observe_calls(lambda: username.enforce("Élise"))
        self.assertEqual(actual, "élise")
        self.assertEqual(calls["derived_property"], 0)

    def test_reuses_normalization_after_a_changed_result_is_readmitted(self):
        password = get_profile("OpaqueString")
        password.enforce("warm")
        actual, calls = observe_calls(lambda: password.enforce("cafe\u0301"))
        self.assertEqual(actual, "café")
        self.assertEqual(calls["normalization_rule"], 1)
        self.assertEqual(calls["enforce"], 3)  # Profile and both class admissions.

    def test_custom_provider_keeps_its_normalization_hook(self):
        class AlternateUnicodeData(UnicodeData):
            def normalize(self, form, value):
                if form == "NFC" and value == "a":
                    return "b"
                return super().normalize(form, value)

        profile = get_profile("UsernameCaseMapped")
        profile.base.ucd = AlternateUnicodeData()
        self.assertEqual(profile.enforce("A"), "b")

    def test_native_admission_preserves_error_order_and_offset(self):
        identifier = get_profile("IdentifierClass")
        freeform = get_profile("FreeFormClass")
        for cls, value, offset, reason in (
            (identifier, "é \x00", 1, "spaces"),
            (identifier, "a\x7f ", 1, "controls"),
            (freeform, "é \x00", 2, "controls"),
            (freeform, "l·l\x00", 3, "controls"),
        ):
            with self.subTest(value=value), self.assertRaises(UnicodeEncodeError) as raised:
                cls.enforce(value)
            error = raised.exception
            self.assertEqual((error.object, error.start, error.end), (value, offset, offset + 1))
            self.assertEqual(error.reason, "DISALLOWED/" + reason)

    def test_an_overridden_native_property_still_controls_admission(self):
        identifier = get_profile("IdentifierClass")
        identifier.enforce("a")
        identifier.ucd.category = lambda _value: "Cn"
        with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/unassigned"):
            identifier.enforce("a")
