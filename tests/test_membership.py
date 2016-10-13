from datetime import date
from unittest import TestCase

import pytest

from .helpers import example_file

from popolo_data.importer import Popolo


EXAMPLE_SINGLE_MEMBERSHIP = b'''
{
    "persons": [
        {
            "id": "SP-937-215",
            "name:": "Jean-Luc Picard"
        }
    ],
    "organizations": [
        {
            "id": "starfleet",
            "name": "Starfleet"
        }
    ],
    "memberships": [
        {
            "person_id": "SP-937-215",
            "organization_id": "starfleet",
            "start_date": "2327-12-01"
        }
    ]
}
'''


class TestMemberships(TestCase):

    def test_empty_file_gives_no_memberships(self):
        with example_file(b'{}') as filename:
            popolo = Popolo.from_filename(filename)
            assert len(popolo.memberships) == 0

    def test_membership_should_not_have_name(self):
        with example_file(EXAMPLE_SINGLE_MEMBERSHIP) as fname:
            popolo = Popolo.from_filename(fname)
            assert len(popolo.memberships) == 1
            m = popolo.memberships[0]
            with pytest.raises(AttributeError):
                m.name

    def test_get_organization_from_membership(self):
        with example_file(EXAMPLE_SINGLE_MEMBERSHIP) as fname:
            popolo = Popolo.from_filename(fname)
            assert len(popolo.memberships) == 1
            m = popolo.memberships[0]
            assert m.start_date == date(2327, 12, 1)

    def test_get_sentinel_end_date_from_membership(self):
        with example_file(EXAMPLE_SINGLE_MEMBERSHIP) as fname:
            popolo = Popolo.from_filename(fname)
            m = popolo.memberships[0]
            assert m.end_date >= date(2500, 1, 1)
