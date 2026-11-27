"""Differential witnesses for compact native admission."""

import unittest

from precis_i18n.baseclass import FreeFormClass, IdentifierClass, _native_common_properties
from precis_i18n.unicode import UnicodeData


class GenericUnicodeData(UnicodeData):
    """Select the generic path with the same Unicode operations."""


def outcome(string_class, value):
    try:
        return string_class.enforce(value)
    except UnicodeEncodeError as error:
        return error.encoding, error.object, error.start, error.end, error.reason


class BulkAdmissionTests(unittest.TestCase):
    def test_native_admission_flags_are_immutable_and_compact(self):
        table = _native_common_properties()
        codes, outcomes = table.codes, table.outcomes
        self.assertIsInstance(codes, bytes)
        self.assertEqual(len(codes), 0x0370)
        self.assertEqual(len(outcomes), len(set(outcomes)))

    def test_complete_bulk_domain_matches_generic_admission(self):
        for cls in (IdentifierClass, FreeFormClass):
            native = cls(UnicodeData())
            generic = cls(GenericUnicodeData())
            for cp in range(0x0370):
                value = "a" * 128 + chr(cp) + "\u0301"
                self.assertEqual(outcome(native, value), outcome(generic, value), (cls, cp))
            for value in ("a" * 128 + "l·l", "a" * 128 + "L·L", "a" * 128 + "\u30fb\u30ab"):
                self.assertEqual(outcome(native, value), outcome(generic, value))

    def test_ordinary_and_exceptional_native_characters_match_generic(self):
        inputs = ("漢字", "カ\u3099", "αβ", "Жц", "aא", "الإ", "\u2163", "\u1100", "\u115f",
                  "\u3164", "\ud7ca", "\ufdd0", "\U0010ffff", "\u200d", "\u302e", "\ufeff",
                  "a\u0661\u06f1", "\u0375α", "\u0375漢", "\U00010400", "\ud800", "Ａ")
        for cls in (IdentifierClass, FreeFormClass):
            native = cls(UnicodeData())
            generic = cls(GenericUnicodeData())
            for value in inputs:
                self.assertEqual(outcome(native, value), outcome(generic, value), (cls, value))
