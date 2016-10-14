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
            popolo = Popolo.from_filename(filename)
            assert len(popolo.persons) == 0

    def test_single_person_name(self):
        with example_file(b'{"persons": [{"name": "Harry Truman"}]}') as fname:
            popolo = Popolo.from_filename(fname)
            assert len(popolo.persons) == 1
            person = popolo.persons[0]
            assert person.name == 'Harry Truman'
            assert person.name_at(date(2016, 1, 11)) == 'Harry Truman'

    def test_get_first_person(self):
        with example_file(EXAMPLE_TWO_PEOPLE) as fname:
            popolo = Popolo.from_filename(fname)
            assert len(popolo.persons) == 2
            person = popolo.persons.first
            assert person.name == 'Norma Jennings'
            assert person.id == "1"

    def test_person_equality_and_inequality(self):
        with example_file(EXAMPLE_TWO_PEOPLE) as fname:
            person_norma_a = Popolo.from_filename(fname).persons[0]
            person_norma_b = Popolo.from_filename(fname).persons[0]
            person_harry = Popolo.from_filename(fname).persons[1]
            assert person_norma_a == person_norma_b
            assert not (person_norma_a != person_norma_b)
            assert person_harry == person_harry
            assert not (person_norma_a == person_harry)
            assert person_norma_a != person_harry

    def test_first_from_empty_file_returns_none(self):
        with example_file(b'{}') as filename:
            popolo = Popolo.from_filename(filename)
            assert popolo.persons.first == None

    def test_filter_of_people_none_matching(self):
        with example_file(EXAMPLE_TWO_PEOPLE) as fname:
            popolo = Popolo.from_filename(fname)
            matches = popolo.persons.filter(name='Dennis the Menace')
            assert len(matches) == 0

    def test_filter_of_people_one_matching(self):
        with example_file(EXAMPLE_TWO_PEOPLE) as fname:
            popolo = Popolo.from_filename(fname)
            matches = popolo.persons.filter(name='Harry Truman')
            assert len(matches) == 1
            assert matches[0].name == 'Harry Truman'

    def test_get_of_people_none_matching(self):
        with example_file(b'{}') as fname:
            popolo = Popolo.from_filename(fname)
            with pytest.raises(Person.DoesNotExist):
                popolo.persons.get(name='Harry Truman')

    def test_get_of_people_multiple_matches(self):
        with example_file(EXAMPLE_TWO_PEOPLE) as fname:
            popolo = Popolo.from_filename(fname)
            with pytest.raises(Person.MultipleObjectsReturned):
                popolo.persons.get(national_identity='American')

    def test_get_of_people_one_matching(self):
        with example_file(EXAMPLE_TWO_PEOPLE) as fname:
            popolo = Popolo.from_filename(fname)
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
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            assert person.wikidata == 'Q1343162'
            assert person.image == 'http://twin-peaks.example.org/harry.jpg'
            assert person.identifiers == [
                {
                    'scheme': 'wikidata',
                    'identifier': 'Q1343162'
                }
            ]

    def test_person_repr(self):
        with example_file(b'{"persons": [{"name": "Paul l\'Astnam\u00e9"}]}') as fname:
            popolo = Popolo.from_filename(fname)
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
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            assert person.twitter == \
                'https://twitter.com/notarealtwitteraccountforharry'

    def test_person_contact_detail_twitter_and_contact_details_list(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman",
            "contact_details": [
                {
                    "type": "twitter",
                    "value": "notarealtwitteraccountforharry"
                },
                {
                    "type": "phone",
                    "value": "555-5555"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            assert person.twitter == \
                'notarealtwitteraccountforharry'
            assert person.contact_details == [
                {
                    "type": "twitter",
                    "value": "notarealtwitteraccountforharry"
                },
                {
                    "type": "phone",
                    "value": "555-5555"
                }
            ]

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
            popolo = Popolo.from_filename(fname)
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
            "summary": "He assists Dale Cooper in the Laura Palmer case",
            "given_name": "Harry",
            "family_name": "Truman"
        }
    ]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            assert person.name == "Harry Truman"
            assert person.email == "harry@example.org"
            assert person.image == "http://twin-peaks.example.org/harry.jpg"
            assert person.gender == "male"
            assert person.honorific_prefix == "Sheriff"
            assert person.honorific_suffix == "Bookhouse Boy"
            assert person.biography == "Harry S. Truman is the sheriff of Twin Peaks"
            assert person.summary == "He assists Dale Cooper in the Laura Palmer case"
            assert person.given_name == "Harry"
            assert person.family_name == "Truman"

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
            popolo = Popolo.from_filename(fname)
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
            popolo = Popolo.from_filename(fname)
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
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            assert person.phone == '9304832'
            assert person.fax == '9304833'

    def test_person_facebook_and_links_list(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Harry Truman",
            "links": [
                {
                    "note": "facebook",
                    "url": "https://facebook.example.com/harry-s-truman"
                },
                {
                    "note": "wikia",
                    "url": "http://twinpeaks.wikia.com/wiki/Harry_S._Truman"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            assert person.facebook == \
                'https://facebook.example.com/harry-s-truman'
            assert person.links == [
                {
                    "note": "facebook",
                    "url": "https://facebook.example.com/harry-s-truman"
                },
                {
                    "note": "wikia",
                    "url": "http://twinpeaks.wikia.com/wiki/Harry_S._Truman"
                }
            ]

    def test_person_images(self):
        with example_file(u'''
{
    "persons": [
        {
            "name": "Бганба Валерий Рамшухович",
            "images": [
                {
                    "url": "http://www.parlamentra.org/upload/iblock/b85/%D1%80%D0%B0%D0%BC.jpg"
                },
                {
                    "url": "https://upload.wikimedia.org/wikipedia/commons/a/a3/Бганба_Валерий_Рамшухович.jpg"
                }
            ]
        }
    ]
}
'''.encode('utf-8')) as fname:
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            assert person.images == [
                {'url': 'http://www.parlamentra.org/upload/iblock/b85/%D1%80%D0%B0%D0%BC.jpg'},
                {'url': u'https://upload.wikimedia.org/wikipedia/commons/a/a3/\u0411\u0433\u0430\u043d\u0431\u0430_\u0412\u0430\u043b\u0435\u0440\u0438\u0439_\u0420\u0430\u043c\u0448\u0443\u0445\u043e\u0432\u0438\u0447.jpg'}
            ]

    def test_person_other_names(self):
        with example_file(b'''
{
    "persons": [
        {
            "id": "john-q-public",
            "name": "Mr. John Q. Public, Esq.",
            "other_names": [
                {
                    "name": "Mr. Ziggy Q. Public, Esq.",
                    "start_date": "1920-01",
                    "end_date": "1949-12-31",
                    "note": "Birth name"
                },
                {
                    "name": "Dragonsbane",
                    "note": "LARP character name"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            assert person.other_names == [
                {
                    'end_date': '1949-12-31',
                    'name': 'Mr. Ziggy Q. Public, Esq.',
                    'note': 'Birth name',
                    'start_date': '1920-01'
                },
                {
                    "name": "Dragonsbane",
                    "note": "LARP character name"
                }
            ]

    def test_person_sources(self):
        with example_file(b'''
{
    "persons": [
        {
            "id": "john-q-public",
            "name": "Mr. John Q. Public, Esq.",
            "sources": [
                {
                    "note": "His homepage",
                    "url": "http://example.org/john-q-public"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            assert person.sources == [
                {
                    'note': 'His homepage',
                    'url': 'http://example.org/john-q-public'
                }
            ]

    def test_person_name_at_no_historic(self):
        # I don't quite understand why this behaviour is desirable,
        # but it's the logic of the Ruby version. TODO: check this.
        with example_file(b'''
{
    "persons": [
        {
            "name": "Bob",
            "other_names": [
                {
                    "name": "Robert",
                    "start_date": "2000-01-01"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            assert person.name_at(date(2016, 1, 11)) == 'Bob'

    def test_person_name_at_historic(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Bob",
            "other_names": [
                {
                    "name": "Robert",
                    "start_date": "1989-01-01",
                    "end_date": "1999-12-31"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            assert person.name_at(date(1990, 6, 1)) == 'Robert'

    def test_person_multiple_names_at_one_date(self):
        with example_file(b'''
{
    "persons": [
        {
            "name": "Bob",
            "other_names": [
                {
                    "name": "Robert",
                    "start_date": "1989-01-01",
                    "end_date": "1999-12-31"
                },
                {
                    "name": "Bobby",
                    "start_date": "1989-01-01",
                    "end_date": "2012-12-31"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            person = popolo.persons.first
            with pytest.raises(Exception) as excinfo:
                person.name_at(date(1996, 1, 1))
            assert str("Multiple names for <Person: Bob> found at date 1996-01-01") in \
                str(excinfo)
