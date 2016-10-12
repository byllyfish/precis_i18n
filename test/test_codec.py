import unittest
import precis_i18n.codec


class TestCodec(unittest.TestCase):
    def test_encode(self):
        self.assertEqual('Juliet'.encode('UsernameCasePreserved'), b'Juliet')
        self.assertEqual('Juliet'.encode('UsernameCaseMapped'), b'juliet')
        self.assertEqual(' pass \u1FBF\u3000'.encode('OpaqueString'),
                         b' pass \xe1\xbe\xbf ')
        self.assertEqual(' Juliet '.encode('NicknameCaseMapped'), b'juliet')
        self.assertEqual('Juliet'.encode('IdentifierClass'), b'Juliet')
        self.assertEqual('Juliet'.encode('FreeFormClass'), b'Juliet')


    def test_decode(self):
        with self.assertRaises(NotImplementedError):
            b'Juliet'.decode('UsernameCasePreserved')

    def test_encode_errors(self):
        # errors must be 'strict'; 'replace' and others are not supported.
        with self.assertRaises(ValueError):
            'Juliet'.encode('opaquestring', errors='replace')
        # non-matching codec names shouldn't work.
        with self.assertRaises(LookupError):
            'Juliet'.encode('opaquestring_nonexistant')
