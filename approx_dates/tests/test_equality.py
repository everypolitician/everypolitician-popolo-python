from approx_dates.models import ApproxDate

from datetime import date
from unittest import TestCase


class TestApproxDateEquality(TestCase):

    def test_equality_true_to_other_approxdate(self):
        d1 = ApproxDate.from_iso8601('1964-06-26')
        d2 = ApproxDate.from_iso8601('1964-06-26')
        assert d1 == d2

    def test_equality_false_to_other_approxdate(self):
        d1 = ApproxDate.from_iso8601('1964-06-26')
        d2 = ApproxDate.from_iso8601('1977-12-27')
        assert not (d1 == d2)

    def test_inequality_true_to_other_approxdate(self):
        d1 = ApproxDate.from_iso8601('1964-06-26')
        d2 = ApproxDate.from_iso8601('1977-12-27')
        assert d1 != d2

    def test_inequality_false_to_other_approxdate(self):
        d1 = ApproxDate.from_iso8601('1964-06-26')
        d2 = ApproxDate.from_iso8601('1964-06-26')
        assert not (d1 != d2)

    # Test comparing to different precisions:

    def test_equality_false_to_different_precision(self):
        d1 = ApproxDate.from_iso8601('1964-06-26')
        d2 = ApproxDate.from_iso8601('1964-06')
        assert not (d1 == d2)

    def test_inequality_true_to_different_precision(self):
        d1 = ApproxDate.from_iso8601('1964-06-26')
        d2 = ApproxDate.from_iso8601('1964-06')
        assert (d1 != d2)

    # Test equality to datetime.date, only if it's precise:

    def test_equality_false_between_precise_and_date(self):
        approx_date = ApproxDate.from_iso8601('1964-06-26')
        datetime_date = date(1964, 6, 26)
        assert approx_date == datetime_date

    def test_equality_false_between_precise_and_different_date(self):
        approx_date = ApproxDate.from_iso8601('1964-06-26')
        datetime_date = date(1964, 6, 10)
        assert not (approx_date == datetime_date)

    def test_equality_false_between_imprecise_and_date_in_range(self):
        approx_date = ApproxDate.from_iso8601('1964-06')
        datetime_date = date(1964, 6, 26)
        assert not (approx_date == datetime_date)

    def test_equality_false_between_imprecise_and_date_out_of_range(self):
        approx_date = ApproxDate.from_iso8601('1999')
        datetime_date = date(1964, 6, 26)
        assert not (approx_date == datetime_date)
