import unittest

from precis_i18n import get_profile
from precis_i18n.profile import Username
from precis_i18n.unicode import UnicodeData


class IdempotentTestCase(unittest.TestCase):
    def test_broken_profile(self):
        """Test that we can catch a profile that is not idempotent."""

        class _BrokenProfile(Username):
            def additional_mapping_rule(self, value):
                return "%s+" % value

        broken = _BrokenProfile(UnicodeData(), name="Broken")
        with self.assertRaisesRegex(ValueError, "DISALLOWED/not_idempotent"):
            broken.enforce("x")

    def test_all_codepoints(self):
        """Verify all individual code points are idempotent."""
        profiles = [
            get_profile(profile)
            for profile in ("UsernameCaseMapped", "NicknameCaseMapped")
        ]
        for cp in range(0x0110000):
            original = chr(cp)
            for profile in profiles:
                try:
                    profile.enforce(original)
                except UnicodeEncodeError as ex:
                    if "not_idempotent" in str(ex):
                        raise
