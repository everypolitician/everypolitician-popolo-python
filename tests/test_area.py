# -*- coding: utf-8 -*-

from unittest import TestCase

from popolo_data.importer import Popolo


EXAMPLE_AREA = {
    "id": "area/tartu_linn",
    "identifiers": [
        {
            "identifier": "Q3032626",
            "scheme": "wikidata"
        }
    ],
    "name": "Tartu linn",
    "other_names": [
        {
            "lang": "fr",
            "name": "Dixième circonscription législative d'Estonie",
            "note": "multilingual"
        },
        {
            "lang": "et",
            "name": "Valimisringkond nr 10",
            "note": "multilingual"
        },
        {
            "lang": "en",
            "name": "Electoral District 10 (Tartu)",
            "note": "multilingual"
        }
    ],
    "type": "constituency"
}


class TestAreas(TestCase):

    def test_empty_file_gives_no_areas(self):
        popolo = Popolo({})
        assert len(popolo.areas) == 0

    def test_single_area_with_name(self):
        popolo = Popolo({"areas": [EXAMPLE_AREA]})
        assert len(popolo.areas) == 1
        area = popolo.areas[0]
        assert area.name == 'Tartu linn'

    def test_area_type(self):
        popolo = Popolo({"areas": [EXAMPLE_AREA]})
        area = popolo.areas[0]
        assert area.type == 'constituency'

    def test_area_identifiers(self):
        popolo = Popolo({"areas": [EXAMPLE_AREA]})
        area = popolo.areas[0]
        assert area.identifiers == [
            {
                "identifier": "Q3032626",
                "scheme": "wikidata"
            }
        ]
