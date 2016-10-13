import unittest
import precis_i18n.codec
import os
import json

HERE = os.path.abspath(os.path.dirname(__file__))
GOLDEN = os.path.join(HERE, 'examples.txt')
GOLDEN_JSON = os.path.join(HERE, 'golden.json')

UCD_VERSION = precis_i18n.get_profile('FreeFormClass').ucd.version


class TestGolden(unittest.TestCase):

    def test_golden_file(self):
        for profile, allow, input, expected in _read_golden():
            if allow:
                self.check_allow(profile, input, expected)
            else:
                self.check_disallow(profile, input, expected)

    def test_golden_json(self):
        with open(GOLDEN_JSON, encoding='ascii') as input_file:
            entries = json.load(input_file)

        for entry in entries:
            if 'unicode_version' in entry and UCD_VERSION < entry['unicode_version']:
                continue
            profile, input, output, error = (entry['profile'], entry['input'], entry['output'], entry['error'])
            if not error:
                self.check_allow(profile, input, output)
            else:
                self.check_disallow(profile, input, error)

    def check_allow(self, profile, input, expected):
        #print('check_allow', profile, input)
        actual = input.encode(profile).decode('utf-8')
        self.assertEqual(actual, expected)
        # Check that the profile encoding is idempotent. If the following 
        # assertion fails, the profile is not idempotent.
        idempotent = actual.encode(profile).decode('utf-8')
        if idempotent != actual:
            print('\n"%s" not idempotent: "%s" => "%s" => "%s"' % (profile, _escape(input), _escape(actual), _escape(idempotent)))
        # The Nickname profile is not idempotent?
        if not profile.lower().startswith('nickname'):
            self.assertEqual(idempotent, actual)
        

    def check_disallow(self, profile, input, expected):
        #print('check_disallow', profile, input)
        with self.assertRaisesRegex(UnicodeEncodeError, expected):
            input.encode(profile)



def _read_golden():
    """ Generator function to return 4-tuples with test data:
    
        (profile, allow, input, expected)

    e.g. ('UsernameCaseMapped', True, 'Kevin', 'kevin')
    """
    with open(GOLDEN, encoding='utf-8') as golden:
        for line in golden:
            fields = [_unescape(s) for s in line.strip().split()]
            if len(fields) == 0 or fields[0].startswith('#'):
                continue
            if len(fields) == 2:
                fields.append(fields[1])

            cmd = fields[0].upper()
            if cmd == 'PROFILE':
                profile = fields[1]
            elif cmd == 'ALLOW':
                yield (profile, True, fields[1], fields[2])
            elif cmd == 'DISALLOW':
                if len(fields) == 2:
                    fields.append('')
                yield (profile, False, fields[1], fields[2])


def _unescape(s):
    return s.encode('raw-unicode-escape').decode('unicode_escape')


def _escape(s):
    return s.encode('unicode_escape').decode('ascii')


if __name__ == '__main__':
    unittest.main(verbosity=2)
