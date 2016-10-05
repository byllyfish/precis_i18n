import unittest
from precis_i18n.codepointset import CodepointSet


class TestCodepointSet(unittest.TestCase):
    
    def test_contains(self):
        cps = CodepointSet('0000\n')
        actual = [cp in cps for cp in range(-1, 4)]
        self.assertEqual(actual, [False, True, False, False, False])

        self.assertFalse(0x010FFFF in cps)

        cps = CodepointSet('0000..0001\n')
        actual = [cp in cps for cp in range(-1, 4)]
        self.assertEqual(actual, [False, True, True, False, False])

        cps = CodepointSet('0000\n0001\n0002')
        actual = [cp in cps for cp in range(-1, 4)]
        self.assertEqual(actual, [False, True, True, True, False])

        cps = CodepointSet('0000\n0002')
        actual = [cp in cps for cp in range(-1, 4)]
        self.assertEqual(actual, [False, True, False, True, False])

        cps = CodepointSet('10000..10FFFF')
        self.assertTrue(0x10FFFF in cps)
        self.assertFalse(0x110000 in cps)

    def test_equals(self):
        cps = CodepointSet('0000..00FF')
        self.assertEqual(cps, CodepointSet('0000..00FF'))
        self.assertNotEqual(cps, CodepointSet('0000..00FE'))

    def test_repr(self):
        cps = CodepointSet('')
        self.assertEqual(repr(cps), "CodepointSet('')")

        cps = CodepointSet('0000')
        self.assertEqual(repr(cps), "CodepointSet('0000')")

        cps = CodepointSet('0000..00FF')
        self.assertEqual(repr(cps), "CodepointSet('0000..00FF')")

        cps = CodepointSet('0001..FFFF\n100000..10FFFF')
        self.assertEqual(repr(cps), r"CodepointSet('0001..FFFF\n100000..10FFFF')")

        cps = CodepointSet('FFFF..1FFFF')
        self.assertEqual(repr(cps), "CodepointSet('FFFF..1FFFF')")

        cps = CodepointSet('10000..1FFFF')
        self.assertEqual(repr(cps), "CodepointSet('10000..1FFFF')")

        cps = CodepointSet('FFFE\n10000..1FFFF')
        self.assertEqual(repr(cps), r"CodepointSet('FFFE\n10000..1FFFF')")

    def test_coalesce(self):
        cps = CodepointSet('0000\n0001\n0002')
        self.assertEqual(cps, CodepointSet('0000..0002'))

        cps = CodepointSet('0000\n0002\n0003..0004')
        self.assertEqual(cps, CodepointSet('0000\n0002..0004'))

    def test_malformed_range(self):
        with self.assertRaises(ValueError):
            CodepointSet('0002..0000\n0001')

        with self.assertRaises(ValueError):
            CodepointSet('0000..0001\n0000..0001\n0002')

        with self.assertRaises(ValueError):
            CodepointSet('0000\n0002\n0002..0004')

        with self.assertRaises(ValueError):
            CodepointSet('110000')

        with self.assertRaises(ValueError):
            CodepointSet('0000\n000G')


    def test_even_odd(self):
        data = '\n'.join("%04X" % cp for cp in range(0, 10000, 2))
        cps = CodepointSet(data)
        for cp in range(10000):
            if cp in cps:
                self.assertTrue((cp % 2) == 0)
            else:
                self.assertFalse((cp % 2) == 0)

    def test_parse(self):
        cps = CodepointSet('A\nBB\n')
        self.assertEqual(repr(cps), r"CodepointSet('000A\n00BB')")

        cps = CodepointSet('AAA\nBBB..CCC\n')
        self.assertEqual(repr(cps), r"CodepointSet('0AAA\n0BBB..0CCC')")

        cps = CodepointSet('\n  \n # comment  \n   \n')
        self.assertEqual(repr(cps), "CodepointSet('')")
