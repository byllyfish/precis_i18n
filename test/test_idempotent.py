import unittest
from precis_i18n.factory import UCD
from precis_i18n.profile import Username


class IdempotentTestCase(unittest.TestCase):
    def test_broken_profile(self):
        """Test that we can catch a profile that is not idempotent.
        """

        class _BrokenProfile(Username):
            def additional_mapping_rule(self, value):
                return '%s+' % value

        broken = _BrokenProfile(UCD, name='Broken')
        with self.assertRaisesRegex(ValueError, 'DISALLOWED/not_idempotent'):
            broken.enforce('x')
