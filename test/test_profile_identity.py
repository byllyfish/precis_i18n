"""Public identity and explicit Unicode version selection."""

import unicodedata
import unittest

from precis_i18n import get_profile, get_profile_identity
from precis_i18n.unicode import UnicodeData


class DatabaseProxy:
    unidata_version = unicodedata.unidata_version
    category = staticmethod(unicodedata.category)
    combining = staticmethod(unicodedata.combining)
    bidirectional = staticmethod(unicodedata.bidirectional)
    normalize = staticmethod(unicodedata.normalize)


class TestProfileIdentity(unittest.TestCase):
    def test_identity_is_stable_and_immutable(self):
        first = get_profile_identity(get_profile("UsernameCaseMapped"))
        second = get_profile_identity(get_profile("usernamecasemapped"))
        self.assertEqual(first, second)
        self.assertEqual(first.fingerprint, second.fingerprint)
        self.assertEqual(first.unicode_version, unicodedata.unidata_version)
        self.assertEqual(first.profile, "UsernameCaseMapped")
        self.assertEqual(len(first.fingerprint), 64)
        with self.assertRaises(AttributeError):
            setattr(first, "unicode_version", "0.0.0")

    def test_different_profile_policies_have_different_identities(self):
        profiles = tuple(
            get_profile_identity(get_profile(name))
            for name in ("UsernameCaseMapped", "UsernameCaseMapped:CaseFold",
                         "UsernameCasePreserved", "NicknameCasePreserved", "OpaqueString",
                         "IdentifierClass", "FreeFormClass")
        )
        self.assertEqual(len({identity.fingerprint for identity in profiles}), len(profiles))
        self.assertEqual(profiles[0].case_mapping, "lowercase")
        self.assertEqual(profiles[1].case_mapping, "casefold")
        self.assertEqual(profiles[3].case_mapping, "none")
        self.assertEqual(profiles[3].comparison_case_mapping, "lowercase")

    def test_legacy_provider_mode_cannot_attest_the_native_identity(self):
        native = get_profile_identity(get_profile("UsernameCaseMapped"))
        alternate = get_profile_identity(get_profile("UsernameCaseMapped", unicodedata=DatabaseProxy()))
        self.assertEqual(native.unicode_version, alternate.unicode_version)
        self.assertEqual(alternate.execution_mode, "legacy")
        self.assertIsNone(alternate.fingerprint)
        self.assertNotEqual(native.fingerprint, alternate.fingerprint)

    def test_replacing_the_unicode_adapter_invalidates_the_captured_identity(self):
        class AlternateLower(UnicodeData):
            def lower(self, value):
                return value

        for adapter in (UnicodeData(DatabaseProxy()), AlternateLower()):
            with self.subTest(mode=adapter.mode):
                profile = get_profile("UsernameCaseMapped")
                profile.base.ucd = adapter
                with self.assertRaisesRegex(ValueError, "Unicode data has changed"):
                    get_profile_identity(profile)

    def test_requested_unicode_version_cannot_silently_fall_back(self):
        requested = "18.0.0" if unicodedata.unidata_version != "18.0.0" else "17.0.0"
        with self.assertRaises(ValueError):
            get_profile("UsernameCaseMapped", unicode_version=requested)

    def test_provider_failure_is_isolated_between_enforcements(self):
        class FailingProvider(DatabaseProxy):
            @staticmethod
            def normalize(form, value):
                if value == "x":
                    raise RuntimeError("Synthetic provider failure")
                return unicodedata.normalize(form, value)

        profile = get_profile("UsernameCaseMapped", unicodedata=FailingProvider())
        with self.assertRaisesRegex(RuntimeError, "Synthetic provider failure"):
            profile.enforce("x")
        self.assertEqual(profile.enforce("SAFE"), "safe")

    def test_bare_string_classes_offer_exact_keys_without_profile_mapping(self):
        identifier = get_profile("IdentifierClass")
        freeform = get_profile("FreeFormClass")
        self.assertEqual(identifier.comparison_key("Straße"), "Straße".encode("utf-8"))
        self.assertEqual(freeform.comparison_key(b"Stra\xc3\x9fe"), b"Stra\xc3\x9fe")
        self.assertNotEqual(freeform.comparison_key("Ａ"), freeform.comparison_key("A"))
        with self.assertRaises(UnicodeEncodeError):
            identifier.comparison_key("\u212a")
