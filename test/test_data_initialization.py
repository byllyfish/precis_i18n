"""Qualification of immutable Unicode table construction."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event
import unittest
from unittest.mock import patch

from precis_i18n import _unicode_tables
from precis_i18n.codepointset import CodepointSet


class TableConstructionTests(unittest.TestCase):
    def test_sorted_ranges_match_the_text_constructor(self):
        ranges = ((0, 2), (3, 3), (0x10000, 0x10001), (0x10FFFF, 0x10FFFF))
        direct = CodepointSet._from_sorted_ranges(ranges)
        expected = CodepointSet("0000..0003\n10000..10001\n10FFFF")
        self.assertEqual(direct, expected)
        self.assertEqual(tuple(direct.items()), tuple(expected.items()))
        for invalid in (((0, 2), (2, 3)), ((3, 3), (0, 2)), ((0, 0x110000),)):
            with self.assertRaises(ValueError):
                CodepointSet._from_sorted_ranges(invalid)

    def test_concurrent_load_shares_one_object_and_failed_load_can_retry(self):
        original = _unicode_tables.get_data
        entered = Event()
        release = Event()
        attempts = []

        def read(package, filename):
            attempts.append(filename)
            if len(attempts) == 1:
                return None
            entered.set()
            if not release.wait(5):
                raise RuntimeError("Timed out waiting for table loader")
            return original(package, filename)

        with patch.object(_unicode_tables, "_LOADED", {}), patch.object(_unicode_tables, "get_data", read):
            with self.assertRaisesRegex(RuntimeError, "Missing bundled Unicode data"):
                _unicode_tables.load("17.0.0")
            with ThreadPoolExecutor(max_workers=4) as pool:
                first = pool.submit(_unicode_tables.load, "17.0.0")
                self.assertTrue(entered.wait(5))
                others = [pool.submit(_unicode_tables.load, "17.0.0") for _ in range(3)]
                release.set()
                data = first.result(timeout=5)
                for future in others:
                    self.assertIs(future.result(timeout=5), data)
            self.assertEqual(len(attempts), 2)
