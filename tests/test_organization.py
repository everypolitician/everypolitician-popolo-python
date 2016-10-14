# -*- coding: utf-8 -*-

from datetime import date
from unittest import TestCase

import pytest
import six

from .helpers import example_file

from popolo_data.base import MultipleObjectsReturned
from popolo_data.importer import Popolo


class TestOrganizations(TestCase):

    def test_empty_file_gives_no_organizations(self):
        with example_file(b'{}') as filename:
            popolo = Popolo.from_filename(filename)
            assert len(popolo.organizations) == 0

    def test_single_organization_name(self):
        with example_file(
                b'''
{
    "organizations": [{"name": "Starfleet"}]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            assert o.name == 'Starfleet'

    def test_wikidata_property_and_id(self):
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
            popolo = Popolo.from_filename(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            assert o.wikidata == 'Q288523'
            assert o.id == 'starfleet'

    def test_identifiers_list(self):
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
                    "identifier": "123456",
                    "scheme": "made-up-id"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            assert o.identifiers == [
                {
                    'identifier': 'Q288523',
                    'scheme': 'wikidata',
                },
                {
                    'identifier': '123456',
                    'scheme': 'made-up-id',
                },
            ]

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
            popolo = Popolo.from_filename(fname)
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
            popolo = Popolo.from_filename(fname)
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
            popolo = Popolo.from_filename(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            with pytest.raises(MultipleObjectsReturned):
                o.wikidata

    def test_organization_repr(self):
        with example_file(b'{"organizations": [{"name": "M\u00e9decins Sans Fronti\u00e8res"}]}') as fname:
            popolo = Popolo.from_filename(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            if six.PY2:
                assert repr(o) == b"<Organization: M\xc3\xa9decins Sans Fronti\xc3\xa8res>"
            else:
                assert repr(o) == u"<Organization: Médecins Sans Frontières>"

    def test_organization_image(self):
        popolo = Popolo({
            'organizations': [
                {
                    'name': 'ACME corporation',
                    'image': 'http://example.org/acme.jpg',
                }
            ]})
        o = popolo.organizations.first
        assert o.image == 'http://example.org/acme.jpg'

    def test_organization_seats(self):
        popolo = Popolo({
            'organizations': [
                {
                    'name': 'House of Commons',
                    'seats': 650,
                }
            ]})
        o = popolo.organizations.first
        assert o.seats == 650

    def test_organization_founding_and_dissolution_dates(self):
        popolo = Popolo({
            'organizations': [
                {
                    'name': 'ACME corporation',
                    'founding_date': '1950-01-20',
                    'dissolution_date': '2000-11-15',
                }
            ]})
        o = popolo.organizations.first
        assert o.founding_date == date(1950, 1, 20)
        assert o.dissolution_date == date(2000, 11, 15)

    def test_organization_other_names(self):
        with example_file(b'''
{
    "organizations": [
        {
             "id": "abc-inc",
             "name": "ABC, Inc.",
             "other_names": [
                 {
                     "name": "Bob's Diner",
                     "start_date": "1950-01-01",
                     "end_date": "1954-12-31"
                 },
                 {
                     "name": "Joe's Diner",
                     "start_date": "1955-01-01"
                 },
                 {
                     "name": "Famous Joe's"
                 }
             ]
        }
    ]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            assert o.other_names == [
                {
                    'name': "Bob's Diner",
                    'start_date': '1950-01-01',
                    'end_date': '1954-12-31'
                 },
                 {
                     'name': "Joe's Diner",
                     'start_date': '1955-01-01'
                 },
                 {
                     'name': "Famous Joe's"
                 }
            ]

    def test_organization_links_list(self):
        with example_file(
                b'''
{
    "organizations": [
        {
            "id": "starfleet",
            "name": "Starfleet",
            "links": [
                {
                    "url": "https://en.wikipedia.org/wiki/Starfleet",
                    "note": "Wikipedia"
                },
                {
                    "url": "http://memory-alpha.wikia.com/wiki/Starfleet",
                    "note": "Memory Alpha"
                }
            ]
        }
    ]
}
''') as fname:
            popolo = Popolo.from_filename(fname)
            assert len(popolo.organizations) == 1
            o = popolo.organizations[0]
            assert o.links == [
                {
                    'url': 'https://en.wikipedia.org/wiki/Starfleet',
                    'note': 'Wikipedia',
                },
                {
                    'url': 'http://memory-alpha.wikia.com/wiki/Starfleet',
                    'note': 'Memory Alpha',
                },
            ]

    def test_organisation_equality(self):
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
            o_a = Popolo.from_filename(fname).organizations[0]
            o_b = Popolo.from_filename(fname).organizations[0]
            assert o_a == o_b
            assert not (o_a != o_b)
