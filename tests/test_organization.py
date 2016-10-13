# -*- coding: utf-8 -*-

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
            popolo = Popolo.from_filename(fname)
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
