"""Exercise the Unicode provider boundary using independent UCD examples."""

import sys
from types import ModuleType
import unicodedata
import unittest
from unittest.mock import patch

from precis_i18n import get_profile
from precis_i18n.unicode import UnicodeData


class FixtureProvider:
    """Minimal API witness for selecting a provider without an optional dependency."""

    unidata_version = "17.0.0"
    precis_data_identity = "synthetic-test-ucd-v1"
    category = staticmethod(unicodedata.category)
    combining = staticmethod(unicodedata.combining)
    bidirectional = staticmethod(unicodedata.bidirectional)
    normalize = staticmethod(unicodedata.normalize)


class UnicodeModeTests(unittest.TestCase):
    def test_literal_width_decompositions(self):
        ucd = UnicodeData()
        self.assertEqual(ucd.width_map("Ａ　￣ﾡￂｶﾞ"), "A \u00af\u3131\u314f\u30ab\u3099")
        self.assertEqual(ucd.width_map("ＡKÅﬁ①a"), "AKÅﬁ①a")

    def test_literal_width_mapping_cannot_bootstrap_identifier_admission(self):
        profile = get_profile("UsernameCaseMapped")
        with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/has_compat"):
            profile.enforce("ﾡￂ")
        with self.assertRaisesRegex(UnicodeEncodeError, "DISALLOWED/spaces"):
            profile.enforce("Na\u3000me")
        self.assertEqual(profile.enforce("Ａｌｉｃｅ"), "alice")
        self.assertEqual(profile.enforce("ｶﾞ"), "ガ")

    def test_versioned_mode_uses_lowercase_and_casefold_from_selected_data(self):
        ucd = UnicodeData(FixtureProvider(), unicode_version="17.0.0")
        self.assertEqual(ucd.mode, "versioned")
        self.assertEqual(ucd.data_version, "17.0.0")
        self.assertEqual(ucd.property_version, "17.0.0")
        self.assertEqual(ucd.lower("\ua7cb\ua7ceA\u03a3\u0301"), "\u0264\ua7cfa\u03c2\u0301")
        self.assertEqual(ucd.lower("A\u03a3\u0301A"), "a\u03c3\u0301a")
        self.assertEqual(ucd.lower("\u0130\u0131I"), "i\u0307\u0131i")
        self.assertEqual(ucd.casefold("Straße\u03c2"), "strasse\u03c3")

    def test_versioned_configuration_rejects_mismatched_and_unavailable_data(self):
        with self.assertRaisesRegex(ValueError, "requires Unicode data 18.0.0"):
            UnicodeData(FixtureProvider(), unicode_version="18.0.0")
        with self.assertRaisesRegex(ValueError, "Unsupported versioned Unicode data"):
            UnicodeData(FixtureProvider(), unicode_version="99.0.0")

    def test_legacy_provider_retains_native_casing_and_identifies_table_generation(self):
        value = "\ua7ce"
        ucd = UnicodeData(FixtureProvider())
        self.assertEqual(ucd.mode, "legacy")
        self.assertEqual(ucd.data_version, "17.0.0")
        self.assertEqual(ucd.property_version, "18.0.0")
        self.assertEqual(ucd.lower(value), value.lower())
        self.assertEqual(ucd.casefold(value), value.casefold())
        self.assertNotEqual(
            ucd.data_identity, UnicodeData(FixtureProvider(), unicode_version="17.0.0").data_identity
        )

    def test_native_provider_retains_native_casing(self):
        ucd = UnicodeData()
        self.assertEqual(ucd.mode, "native")
        self.assertEqual(ucd.data_version, unicodedata.unidata_version)
        self.assertEqual(ucd.lower("İΣ"), "İΣ".lower())
        self.assertEqual(ucd.casefold("İΣ"), "İΣ".casefold())

    def test_unidentified_legacy_provider_cannot_attest_versioned_semantics(self):
        provider = FixtureProvider()
        provider.precis_data_identity = ""
        self.assertFalse(UnicodeData(provider).identity_attestable)
        with self.assertRaisesRegex(ValueError, "requires a stable data identity"):
            UnicodeData(provider, unicode_version="17.0.0")

    def test_versioned_data_identity_includes_the_custom_provider_declaration(self):
        provider = FixtureProvider()
        first = UnicodeData(provider, unicode_version="17.0.0")
        provider.precis_data_identity = "synthetic-test-ucd-v2"
        changed = UnicodeData(provider, unicode_version="17.0.0")
        self.assertTrue(first.identity_attestable)
        self.assertNotEqual(first.data_identity, changed.data_identity)

    def test_versioned_provider_rejects_incoherent_normalization(self):
        class UnorderedDecomposition(FixtureProvider):
            @staticmethod
            def normalize(form, value):
                if form == "NFD" and value == "\u1e0a\u0323":
                    return "D\u0307\u0323"
                return unicodedata.normalize(form, value)

        provider = UnorderedDecomposition()
        self.assertEqual(UnicodeData(provider).mode, "legacy")
        with self.assertRaisesRegex(ValueError, "incompatible normalization"):
            get_profile("UsernameCaseMapped", unicodedata=provider, unicode_version="17.0.0")

    def test_registered_versioned_provider_identity_captures_runtime(self):
        from precis_i18n import unicode as backend

        provider = ModuleType("unicodedata2")
        for attribute in ("unidata_version", "category", "combining", "bidirectional", "normalize"):
            setattr(provider, attribute, getattr(FixtureProvider, attribute))
        with patch.dict(sys.modules, unicodedata2=provider):
            with patch.object(backend, "_unicodedata2_revision", return_value="17.0.1"):
                first = UnicodeData(provider, unicode_version="17.0.0")
                with patch.object(backend, "_RUNTIME_IDENTITY", ("other-runtime-build",)):
                    second = UnicodeData(provider, unicode_version="17.0.0")
        self.assertNotEqual(first.data_identity, second.data_identity)
