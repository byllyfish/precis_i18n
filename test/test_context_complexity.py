"""Work bounds and compatibility of contextual string-class enforcement."""

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import gc
import sys
import unittest
import weakref

from precis_i18n.baseclass import FreeFormClass, IdentifierClass
from precis_i18n.context import context_rule_error
from precis_i18n.unicode import UnicodeData

SIZES = (16, 64, 256, 1024, 4096)


class ObservedString(str):
    """Count examined characters, including those copied by a string slice."""

    def __new__(cls, value, counts):
        result = super().__new__(cls, value)
        result.counts = counts
        return result

    def __iter__(self):
        for char in super().__iter__():
            self.counts["traversed"] += 1
            yield char

    def __getitem__(self, index):
        result = super().__getitem__(index)
        self.counts["traversed"] += len(result)
        if isinstance(index, slice):
            self.counts["copied"] += len(result)
        return result


class ObservedUnicodeData(UnicodeData):
    def __init__(self, counts):
        super().__init__()
        self.counts = counts

    def category(self, char):
        self.counts["category"] += 1
        return super().category(char)

    def hiragana_katakana_han_script(self, cp):
        self.counts["script"] += 1
        return super().hiragana_katakana_han_script(cp)

    def arabic_indic(self, cp):
        self.counts["digits"] += 1
        return super().arabic_indic(cp)

    def extended_arabic_indic(self, cp):
        self.counts["digits"] += 1
        return super().extended_arabic_indic(cp)

    def _join_type(self, cp):
        self.counts["joining"] += 1
        return super()._join_type(cp)


def enforcement_work(value):
    """Count real class validation work without depending on elapsed time."""
    counts = Counter()

    def observe(frame, event, _arg):
        if event == "call" and frame.f_globals["__name__"] == "precis_i18n.context":
            name = frame.f_code.co_name
            if name.startswith("rule_"):
                counts[name] += 1

    string_class = IdentifierClass(ObservedUnicodeData(counts))
    observed = ObservedString(value, counts)
    original_profiler = sys.getprofile()
    sys.setprofile(observe)
    try:
        actual = string_class.enforce(observed)
    finally:
        sys.setprofile(original_profiler)
    if actual != value:
        raise ValueError("String-class enforcement changed the input.")
    return counts


def joining_string(length):
    """Produce completed joining contexts separated by dual-joining characters."""
    contexts = (length - 1) // 4
    return "\u0628\u064e\u200c\u064e" * contexts + "\u0628" * (length - contexts * 4)


class TestContextComplexity(unittest.TestCase):
    def test_katakana_script_is_scanned_once(self):
        for size in SIZES:
            counts = enforcement_work("\u30fb" * (size - 1) + "\u30ab")
            self.assertEqual(counts["category"], size)
            self.assertEqual(counts["script"], size)
            self.assertEqual(counts["rule_katakana_middle_dot"], 1)
            self.assertLessEqual(counts["traversed"], size * 4)

    def test_digit_family_is_scanned_once(self):
        families = (
            ("\u0661", "rule_arabic_indic"),
            ("\u06f1", "rule_extended_arabic_indic"),
        )
        for digit, rule in families:
            for size in SIZES:
                counts = enforcement_work(digit * size)
                self.assertEqual(counts["category"], size)
                self.assertEqual(counts[rule], 1)
                self.assertLessEqual(counts["digits"], size * 3 + 1)
                self.assertLessEqual(counts["traversed"], size * 4)

    def test_repeated_join_controls_do_not_copy_input_slices(self):
        for size in SIZES:
            text = joining_string(size)
            counts = enforcement_work(text)
            self.assertEqual(counts["category"], size)
            self.assertEqual(counts["copied"], 0)
            self.assertEqual(counts["rule_zero_width_nonjoiner"], text.count("\u200c"))
            self.assertLessEqual(counts["joining"], size * 2)
            self.assertLessEqual(counts["traversed"], size * 8)

    def test_transparent_joining_spans_have_linear_work(self):
        for size in SIZES:
            text = "\u0628" + "\u064e" * (size - 3) + "\u200c\u0628"
            counts = enforcement_work(text)
            self.assertEqual(counts["category"], size)
            self.assertEqual(counts["copied"], 0)
            self.assertEqual(counts["joining"], size - 1)
            self.assertLessEqual(counts["traversed"], size * 3)


class TestContextIsolation(unittest.TestCase):
    def test_whole_string_rules_have_separate_verdicts(self):
        string_class = IdentifierClass(UnicodeData())
        with self.assertRaises(UnicodeEncodeError) as raised:
            string_class.enforce("\u30fb\u30ab\u0661\u06f1")
        self.assertEqual(raised.exception.start, 2)
        self.assertEqual(raised.exception.reason, "DISALLOWED/arabic_indic")

    def test_second_nonjoiner_must_have_its_own_context(self):
        text = "\u0628\u200c\u0628a\u200c\u0628"
        database = UnicodeData()
        self.assertEqual(context_rule_error(text, 1, database), "")
        self.assertEqual(context_rule_error(text, 4, database), "zero_width_nonjoiner")
        for string_class in (IdentifierClass(database), FreeFormClass(database)):
            with self.assertRaises(UnicodeEncodeError) as raised:
                string_class.enforce(text)
            self.assertEqual(raised.exception.start, 4)
            self.assertEqual(raised.exception.end, 5)
            self.assertEqual(raised.exception.reason, "DISALLOWED/zero_width_nonjoiner")

    def test_shared_string_class_isolates_context_verdicts(self):
        string_class = IdentifierClass(UnicodeData())
        inputs = [
            ("\u30fb\u30ab", None),
            ("\u30fbA", "DISALLOWED/katakana_middle_dot"),
            ("\u0661\u0662", None),
            ("\u0661\u06f2", "DISALLOWED/arabic_indic"),
            ("\u06f1\u06f2", None),
            ("\u06f1\u0662", "DISALLOWED/extended_arabic_indic"),
        ] * 8

        def enforce(item):
            value, _ = item
            try:
                string_class.enforce(value)
            except UnicodeEncodeError as error:
                return error.reason
            return None

        with ThreadPoolExecutor(max_workers=4) as executor:
            actual = list(executor.map(enforce, inputs))
        self.assertEqual(actual, [expected for _, expected in inputs])

    def test_reused_string_class_does_not_retain_input(self):
        string_class = IdentifierClass(UnicodeData())
        value = ObservedString("\u30fb\u30ab", Counter())
        ref = weakref.ref(value)
        self.assertIs(string_class.enforce(value), value)
        del value
        gc.collect()
        self.assertIsNone(ref())
