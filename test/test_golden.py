import os
import json
import unittest
import precis_i18n.codec

HERE = os.path.abspath(os.path.dirname(__file__))
GOLDEN_JSON = os.path.join(HERE, 'golden.json')

UCD_VERSION = precis_i18n.get_profile('FreeFormClass').ucd.version


class TestGolden(unittest.TestCase):
    def test_golden_json(self):
        with open(GOLDEN_JSON, encoding='ascii') as input_file:
            entries = json.load(input_file)

        for entry in entries:
            if 'unicode_version' in entry and UCD_VERSION < entry[
                    'unicode_version']:
                continue
            profile, input_, output, error = (entry['profile'], entry['input'],
                                              entry['output'], entry['error'])
            if not error:
                self.check_allow(profile, input_, output)
            else:
                self.check_disallow(profile, input_, error)

    def check_allow(self, profile, input_, expected):
        #print('check_allow', profile, input_)
        actual = input_.encode(profile).decode('utf-8')
        self.assertEqual(actual, expected)
        # Check that the profile encoding is idempotent. If the following
        # assertion fails, the profile is not idempotent.
        idempotent = actual.encode(profile).decode('utf-8')
        if idempotent != actual:
            print('\n"%s" not idempotent: "%s" => "%s" => "%s"' %
                  (profile, _escape(input_), _escape(actual),
                   _escape(idempotent)))
        # The Nickname profile is not idempotent?
        if not profile.lower().startswith('nickname'):
            self.assertEqual(idempotent, actual)

    def check_disallow(self, profile, input_, expected):
        #print('check_disallow', profile, input_)
        with self.assertRaisesRegex(UnicodeEncodeError, expected):
            input_.encode(profile)


def _escape(s):
    return s.encode('unicode_escape').decode('ascii')


if __name__ == '__main__':
    unittest.main(verbosity=2)
