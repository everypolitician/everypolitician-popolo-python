from datetime import date
from unittest import TestCase

from approx_dates.models import ApproxDate
from six import text_type


class TestRange(TestCase):

    def test_possibly_in_clearly_between(self):
        d1 = ApproxDate.from_iso8601('2000')
        d2 = ApproxDate.from_iso8601('2005')
        assert ApproxDate.possibly_between(d1, date(2002, 7, 1), d2)

    def test_possibly_in_clearly_before(self):
        d1 = ApproxDate.from_iso8601('2000')
        d2 = ApproxDate.from_iso8601('2005')
        assert not ApproxDate.possibly_between(d1, date(1980, 1, 1), d2)

    def test_possibly_in_clearly_after(self):
        d1 = ApproxDate.from_iso8601('2000')
        d2 = ApproxDate.from_iso8601('2005')
        assert not ApproxDate.possibly_between(d1, date(2010, 12, 31), d2)

    def test_possibly_in_borderline_before(self):
        d1 = ApproxDate.from_iso8601('2000')
        d2 = ApproxDate.from_iso8601('2005')
        assert ApproxDate.possibly_between(d1, date(2000, 7, 1), d2)

    def test_possibly_in_borderline_after(self):
        d1 = ApproxDate.from_iso8601('2000')
        d2 = ApproxDate.from_iso8601('2005')
        assert ApproxDate.possibly_between(d1, date(2005, 7, 1), d2)

    # Also test that real datetime.date objects work:
    def test_datetime_date_between(self):
        d1 = date(2000, 1, 1)
        d2 = date(2005, 12, 31)
        assert ApproxDate.possibly_between(d1, date(2002, 7, 1), d2)

    def test_datetime_date_before(self):
        d1 = date(2000, 1, 1)
        d2 = date(2005, 12, 31)
        assert not ApproxDate.possibly_between(d1, date(2010, 1, 1), d2)

    def test_datetime_date_after(self):
        d1 = date(2000, 1, 1)
        d2 = date(2005, 12, 31)
        assert not ApproxDate.possibly_between(d1, date(1980, 1, 1), d2)
