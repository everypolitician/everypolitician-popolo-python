# -*- coding: utf-8 -*-

from datetime import date
from unittest import TestCase

import pytest
import six

from .helpers import example_file

from popolo_data.importer import Popolo
from popolo_data.base import Person


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

    def test_person_link_twitter(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman",
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

    def test_person_contact_detail_twitter(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman",
            "contact_details": [
                {
                    "type": "twitter",
                    "value": "notarealtwitteraccountforharry"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            person = popolo.persons.first
            assert person.twitter == \
                'notarealtwitteraccountforharry'

    def test_sort_name(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman",
            "sort_name": "Truman"
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            person = popolo.persons.first
            assert person.sort_name == 'Truman'

    def test_simple_person_fields(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman",
            "email": "harry@example.org",
            "image": "http://twin-peaks.example.org/harry.jpg",
            "gender": "male",
            "honorific_prefix": "Sheriff",
            "honorific_suffix": "Bookhouse Boy",
            "biography": "Harry S. Truman is the sheriff of Twin Peaks",
            "summary": "He assists Dale Cooper in the Laura Palmer case"
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            person = popolo.persons.first
            assert person.name == "Harry Truman"
            assert person.email == "harry@example.org"
            assert person.image == "http://twin-peaks.example.org/harry.jpg"
            assert person.gender == "male"
            assert person.honorific_prefix == "Sheriff"
            assert person.honorific_suffix == "Bookhouse Boy"
            assert person.biography == "Harry S. Truman is the sheriff of Twin Peaks"
            assert person.summary == "He assists Dale Cooper in the Laura Palmer case"

    def test_missing_birth_and_death_dates(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman"
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            person = popolo.persons.first
            assert person.birth_date is None
            assert person.death_date is None

    def test_full_birth_and_death_dates(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman",
            "birth_date": "1946-01-24",
            "death_date": "2099-12-31"
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            person = popolo.persons.first
            assert person.birth_date == date(1946, 1, 24)
            assert person.death_date == date(2099, 12, 31)

    def test_phone_and_fax(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman",
            "contact_details": [
                {"type": "phone", "value": "9304832"},
                {"type": "fax", "value": "9304833"}
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            person = popolo.persons.first
            assert person.phone == '9304832'
            assert person.fax == '9304833'

    def test_person_facebook(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman",
            "links": [
                {
                    "note": "facebook",
                    "url": "https://facebook.example.com/harry-s-truman"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo(fname)
            person = popolo.persons.first
            assert person.facebook == \
                'https://facebook.example.com/harry-s-truman'
