from datetime import date
from unittest import TestCase

from approx_dates.models import ApproxDate
from six import text_type


class TestCreation(TestCase):

    def test_create_from_full_iso_8601(self):
        d = ApproxDate.from_iso8601('1964-06-26')
        assert isinstance(d, ApproxDate)
        assert d.earliest_date == date(1964, 6, 26)
        assert d.latest_date == date(1964, 6, 26)
        assert text_type(d) == '1964-06-26'

    def test_create_from_parial_iso_8601_only_year(self):
        d = ApproxDate.from_iso8601('1964')
        assert isinstance(d, ApproxDate)
        assert d.earliest_date == date(1964, 1, 1)
        assert d.latest_date == date(1964, 12, 31)
        assert text_type(d) == '1964'

    def test_create_from_parial_iso_8601_only_year_and_month(self):
        d = ApproxDate.from_iso8601('1964-06')
        assert isinstance(d, ApproxDate)
        assert d.earliest_date == date(1964, 6, 1)
        assert d.latest_date == date(1964, 6, 30)
        assert text_type(d) == '1964-06'

    def test_midpoint_for_precise_date(self):
        d = ApproxDate.from_iso8601('1977-12-27')
        assert d.midpoint_date == date(1977, 12, 27)

    def test_midpoint_for_missing_day(self):
        d = ApproxDate.from_iso8601('1999-12')
        assert d.midpoint_date == date(1999, 12, 16)

    def test_midpoint_for_year(self):
        d = ApproxDate.from_iso8601('2016')
        assert d.midpoint_date == date(2016, 7, 1)

    def test_abritrary_date_range(self):
        d = ApproxDate(date(1926, 1, 3), date(2016, 3, 8))
        assert text_type(d) == '1926-01-03 to 2016-03-08'

    def test_future(self):
        d = ApproxDate.FUTURE
        assert d.earliest_date == date(9999, 12, 31)
        assert d.latest_date == date(9999, 12, 31)
        assert text_type(d) == 'future'

    def test_past(self):
        d = ApproxDate.PAST
        assert d.earliest_date == date(1, 1, 1)
        assert d.latest_date == date(1, 1, 1)
        assert text_type(d) == 'past'
