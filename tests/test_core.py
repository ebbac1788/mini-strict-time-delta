import unittest
from datetime import timedelta

from mini_strict_time_delta import parse, StrictTimeDeltaError


class TestParseHappyPath(unittest.TestCase):
    def test_single_seconds(self):
        self.assertEqual(parse("1s"), timedelta(seconds=1))

    def test_single_minutes(self):
        self.assertEqual(parse("5m"), timedelta(minutes=5))

    def test_single_hours(self):
        self.assertEqual(parse("2h"), timedelta(hours=2))

    def test_single_days(self):
        self.assertEqual(parse("3d"), timedelta(days=3))

    def test_single_milliseconds(self):
        self.assertEqual(parse("500ms"), timedelta(milliseconds=500))

    def test_single_microseconds(self):
        self.assertEqual(parse("100us"), timedelta(microseconds=100))

    def test_long_unit_seconds(self):
        self.assertEqual(parse("1 second"), timedelta(seconds=1))

    def test_long_unit_minutes(self):
        self.assertEqual(parse("5 minutes"), timedelta(minutes=5))

    def test_long_unit_hours(self):
        self.assertEqual(parse("2 hours"), timedelta(hours=2))

    def test_long_unit_days(self):
        self.assertEqual(parse("3 days"), timedelta(days=3))

    def test_long_unit_millis(self):
        self.assertEqual(parse("500 milliseconds"), timedelta(milliseconds=500))

    def test_long_unit_micros(self):
        self.assertEqual(parse("100 microseconds"), timedelta(microseconds=100))

    def test_compound(self):
        self.assertEqual(
            parse("1d 2h 3m 4s 500ms 100us"),
            timedelta(days=1, hours=2, minutes=3, seconds=4,
                      milliseconds=500, microseconds=100),
        )

    def test_multiple_spaces_between_pairs(self):
        self.assertEqual(parse("1h  2m"), timedelta(hours=1, minutes=2))

    def test_zero_value(self):
        self.assertEqual(parse("0s"), timedelta(seconds=0))

    def test_zero_days(self):
        self.assertEqual(parse("0d"), timedelta(0))

    def test_large_seconds(self):
        self.assertEqual(parse("86400s"), timedelta(days=1))


class TestParseErrors(unittest.TestCase):
    def test_empty_string(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("")

    def test_whitespace_only(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("   ")

    def test_leading_space(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse(" 1h")

    def test_trailing_space(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("1h ")

    def test_number_without_unit(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("5")

    def test_unit_without_number(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("h")

    def test_float_value(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("1.5h")

    def test_negative_value(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("-1h")

    def test_plus_sign(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("+1h")

    def test_leading_zero(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("01h")

    def test_double_leading_zero(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("00h")

    def test_unknown_unit(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("5x")

    def test_junk_after_valid(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("1h foo")

    def test_wrong_token_order(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("h1")

    def test_trailing_number(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("1h 2")

    def test_non_string_input(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse(123)

    def test_none_input(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse(None)

    def test_two_consecutive_units(self):
        with self.assertRaises(StrictTimeDeltaError):
            parse("1h m")


class TestParseUnitVariants(unittest.TestCase):
    def test_sec_variant(self):
        self.assertEqual(parse("1 sec"), timedelta(seconds=1))

    def test_min_variant(self):
        self.assertEqual(parse("1 min"), timedelta(minutes=1))

    def test_micro_variant(self):
        self.assertEqual(parse("1 micro"), timedelta(microseconds=1))

    def test_millis_variant(self):
        self.assertEqual(parse("1 millis"), timedelta(milliseconds=1))


if __name__ == "__main__":
    unittest.main()
