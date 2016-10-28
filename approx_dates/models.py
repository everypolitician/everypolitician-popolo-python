from __future__ import unicode_literals

import calendar
from datetime import date
import re

import six


ISO8601_DATE_REGEX_YYYY_MM_DD = \
    re.compile(r'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})$')
ISO8601_DATE_REGEX_YYYY_MM = \
    re.compile(r'^(?P<year>\d{4})-(?P<month>\d{2})$')
ISO8601_DATE_REGEX_YYYY = \
    re.compile(r'^(?P<year>\d{4})$')

_max_date = date(9999, 12, 31)
_min_date = date(1, 1, 1)


@six.python_2_unicode_compatible
class ApproxDate(object):

    def __init__(self, earliest_date, latest_date, source_string=None):
        self.earliest_date = earliest_date
        self.latest_date = latest_date
        self.source_string = source_string

    @classmethod
    def from_iso8601(self, iso8601_date_string):
        full_match = ISO8601_DATE_REGEX_YYYY_MM_DD.search(iso8601_date_string)
        if full_match:
            d = date(*(int(p, 10) for p in full_match.groups()))
            return ApproxDate(d, d, iso8601_date_string)
        no_day_match = ISO8601_DATE_REGEX_YYYY_MM.search(iso8601_date_string)
        if no_day_match:
            year = int(no_day_match.group('year'), 10)
            month = int(no_day_match.group('month'), 10)
            days_in_month = calendar.monthrange(year, month)[1]
            earliest = date(year, month, 1)
            latest = date(year, month, days_in_month)
            return ApproxDate(earliest, latest, iso8601_date_string)
        only_year_match = ISO8601_DATE_REGEX_YYYY.search(iso8601_date_string)
        if only_year_match:
            earliest = date(int(only_year_match.group('year'), 10), 1, 1)
            latest = date(int(only_year_match.group('year'), 10), 12, 31)
            return ApproxDate(earliest, latest, iso8601_date_string)
        msg = "Couldn't parse the ISO 8601 partial date '{0}'"
        raise ValueError(msg.format(iso8601_date_string))

    @property
    def midpoint_date(self):
        delta = self.latest_date - self.earliest_date
        return self.earliest_date + delta / 2

    @property
    def future(self):
        return self.earliest_date == _max_date and self.latest_date == _max_date

    @property
    def past(self):
        return self.earliest_date == _min_date and self.latest_date == _min_date

    def __str__(self):
        if self.source_string is not None:
            return six.text_type(self.source_string)
        if self.future:
            return 'future'
        if self.past:
            return 'past'
        return '{0} to {1}'.format(self.earliest_date, self.latest_date)

    def __eq__(self, other):
        if isinstance(other, date):
            return self.earliest_date == self.latest_date and \
               self.earliest_date == other
        return self.earliest_date == other.earliest_date and \
            self.latest_date == other.latest_date

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def possibly_between(cls, start_date, d, end_date):
        try:
            earlier_bound = start_date.earliest_date
        except AttributeError:
            earlier_bound = start_date
        try:
            later_bound = end_date.latest_date
        except AttributeError:
            later_bound = end_date
        return earlier_bound <= d <= later_bound


ApproxDate.FUTURE = ApproxDate(_max_date, _max_date)
ApproxDate.PAST = ApproxDate(_min_date, _min_date)
