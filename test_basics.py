# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from contextlib import contextmanager
from datetime import date
import os
from tempfile import NamedTemporaryFile
from unittest import TestCase

import pytest
from six import text_type
import six

from popolo_data.base import MultipleObjectsReturned, Person
from popolo_data.importer import Popolo


@contextmanager
def example_file(json_for_file):
    ntf = NamedTemporaryFile(delete=False)
    try:
        ntf.write(json_for_file)
        ntf.close()
        yield ntf.name
    finally:
        os.remove(ntf.name)


class TestLoading(TestCase):

    def test_can_create_from_a_filename(self):
        with example_file(b'{}') as filename:
            Popolo(filename)

    def test_fails_to_create_from_a_nonexistent_filename(self):
        with pytest.raises(IOError) as excinfo:
            Popolo('non-existent-file.json')
        assert 'No such file or directory' in text_type(excinfo)


EXAMPLE_TWO_PEOPLE = b'''
{
    "persons": [
        {
             "id": "1",
             "name": "Norma Jennings",
             "national_identity": "American"
        },
        {
             "id": "2",
             "name": "Harry Truman",
             "national_identity": "American"
        }
    ]
}
'''


class TestPersons(TestCase):

    def test_empty_file_gives_no_people(self):
        with example_file(b'{}') as filename:
            popolo = Popolo(filename)
            assert len(popolo.persons) == 0

    def test_single_person_name(self):
        with example_file(b'{"persons": [{"name": "Harry Truman"}]}') as fname:
            popolo = Popolo(fname)
            assert len(popolo.persons) == 1
            person = popolo.persons[0]
            assert person.name == 'Harry Truman'

    def test_get_first_person(self):
        with example_file(EXAMPLE_TWO_PEOPLE) as fname:
            popolo = Popolo(fname)
            assert len(popolo.persons) == 2
            person = popolo.persons.first
            assert person.name == 'Norma Jennings'
            assert person.id == "1"

    def test_first_from_empty_file_returns_none(self):
        with example_file(b'{}') as filename:
            popolo = Popolo(filename)
            assert popolo.persons.first == None

    def test_filter_of_people_none_matching(self):
        with example_file(EXAMPLE_TWO_PEOPLE) as fname:
            popolo = Popolo(fname)
            matches = popolo.persons.filter(name='Dennis the Menace')
            assert len(matches) == 0

    def test_filter_of_people_one_matching(self):
        with example_file(EXAMPLE_TWO_PEOPLE) as fname:
            popolo = Popolo(fname)
            matches = popolo.persons.filter(name='Harry Truman')
            assert len(matches) == 1
            assert matches[0].name == 'Harry Truman'

    def test_get_of_people_none_matching(self):
        with example_file(b'{}') as fname:
            popolo = Popolo(fname)
            with pytest.raises(Person.DoesNotExist):
                popolo.persons.get(name='Harry Truman')

    def test_get_of_people_multiple_matches(self):
        with example_file(EXAMPLE_TWO_PEOPLE) as fname:
            popolo = Popolo(fname)
            with pytest.raises(Person.MultipleObjectsReturned):
                popolo.persons.get(national_identity='American')

    def test_get_of_people_one_matching(self):
        with example_file(EXAMPLE_TWO_PEOPLE) as fname:
            popolo = Popolo(fname)
            person = popolo.persons.get(name='Harry Truman')
            assert person.id == '2'

    def test_get_person_with_image_and_wikidata(self):
        # n.b. this is actually the Wikidata ID for the actor who
        # played Harry Truman; I couldn't find one for the character.
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman",
            "image": "http://twin-peaks.example.org/harry.jpg",
            "identifiers": [
                {
                    "scheme": "wikidata",
                    "identifier": "Q1343162"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            person = popolo.persons.first
            assert person.wikidata == 'Q1343162'
            assert person.image == 'http://twin-peaks.example.org/harry.jpg'

    def test_person_repr(self):
        with example_file(b'{"persons": [{"name": "Paul l\'Astnam\u00e9"}]}') as fname:
            popolo = Popolo(fname)
            assert len(popolo.persons) == 1
            person = popolo.persons[0]
            if six.PY2:
                assert repr(person) == b"<Person: Paul l'Astnam\xc3\xa9>"
            else:
                assert repr(person) == u"<Person: Paul l'Astnamé>"

    def test_person_contact_detail_twitter(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman",
            "image": "http://twin-peaks.example.org/harry.jpg",
            "links": [
                {
                    "note": "twitter",
                    "url": "https://twitter.com/notarealtwitteraccountforharry"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            person = popolo.persons.first
            assert person.twitter == \
                'https://twitter.com/notarealtwitteraccountforharry'


class TestOrganizations(TestCase):

    def test_empty_file_gives_no_organizations(self):
        with example_file(b'{}') as filename:
            popolo = Popolo(filename)
            assert len(popolo.organizations) == 0

    def test_single_organization_name(self):
        with example_file(
                b'''
{
    "organizations": [{"name": "Starfleet"}]
}
''') as fname:
            popolo = Popolo(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            assert o.name == 'Starfleet'

    def test_wikidata_property(self):
        with example_file(
                b'''
{
    "organizations": [
        {
            "id": "starfleet",
            "name": "Starfleet",
            "identifiers": [
                {
                    "identifier": "Q288523",
                    "scheme": "wikidata"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            assert o.wikidata == 'Q288523'

    def test_classification_property(self):
        with example_file(
                b'''
{
    "organizations": [
        {
            "id": "starfleet",
            "name": "Starfleet",
            "classification": "military"
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            assert o.classification == 'military'

    def test_no_matching_identifier(self):
        with example_file(
                b'''
{
    "organizations": [
        {
            "id": "starfleet",
            "name": "Starfleet"        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations.first
            assert o.wikidata is None

    def test_multiple_identfiers(self):
        with example_file(
                b'''
{
    "organizations": [
        {
            "id": "starfleet",
            "name": "Starfleet",
            "identifiers": [
                {
                    "identifier": "Q288523",
                    "scheme": "wikidata"
                },
                {
                    "identifier": "Q288523-also",
                    "scheme": "wikidata"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            with pytest.raises(MultipleObjectsReturned):
                o.wikidata

    def test_organization_repr(self):
        with example_file(b'{"organizations": [{"name": "M\u00e9decins Sans Fronti\u00e8res"}]}') as fname:
            popolo = Popolo(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            if six.PY2:
                assert repr(o) == b"<Organization: M\xc3\xa9decins Sans Fronti\xc3\xa8res>"
            else:
                assert repr(o) == u"<Organization: Médecins Sans Frontières>"


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
            popolo = Popolo(filename)
            assert len(popolo.memberships) == 0

    def test_membership_should_not_have_name(self):
        with example_file(EXAMPLE_SINGLE_MEMBERSHIP) as fname:
            popolo = Popolo(fname)
            assert len(popolo.memberships) == 1
            m = popolo.memberships[0]
            with pytest.raises(AttributeError):
                m.name

    def test_get_organization_from_membership(self):
        with example_file(EXAMPLE_SINGLE_MEMBERSHIP) as fname:
            popolo = Popolo(fname)
            assert len(popolo.memberships) == 1
            m = popolo.memberships[0]
            assert m.start_date == date(2327, 12, 1)

    def test_get_sentinel_end_date_from_membership(self):
        with example_file(EXAMPLE_SINGLE_MEMBERSHIP) as fname:
            popolo = Popolo(fname)
            m = popolo.memberships[0]
            assert m.end_date >= date(2500, 1, 1)
