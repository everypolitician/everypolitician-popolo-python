from __future__ import unicode_literals

from datetime import date
from unittest import TestCase

from approx_dates.models import ApproxDate
import six

class TestReprMagicMethod(TestCase):

    def test_past(self):
        d = ApproxDate.PAST
        assert repr(d) == 'ApproxDate.PAST'

    def test_future(self):
        d = ApproxDate.FUTURE
        assert repr(d) == 'ApproxDate.FUTURE'

    def test_start_end_no_source(self):
        d = ApproxDate(date(1900, 1, 1,), date(1999, 12, 31))
        assert repr(d) == 'ApproxDate(datetime.date(1900, 1, 1), datetime.date(1999, 12, 31))'

    def test_start_end_source(self):
        d = ApproxDate.from_iso8601('2010-07')
        if six.PY2:
            assert repr(d) == "ApproxDate.from_iso8601(u'2010-07')"
        else:
            assert repr(d) == "ApproxDate.from_iso8601('2010-07')"
