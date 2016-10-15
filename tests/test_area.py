# -*- coding: utf-8 -*-

from unittest import TestCase

import six

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

    def test_area_id(self):
        popolo = Popolo({"areas": [EXAMPLE_AREA]})
        area = popolo.areas[0]
        assert area.id == 'area/tartu_linn'

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

    def test_area_other_names(self):
        popolo = Popolo({"areas": [EXAMPLE_AREA]})
        area = popolo.areas[0]
        assert area.other_names == [
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
        ]

    def test_area_wikidata(self):
        popolo = Popolo({"areas": [EXAMPLE_AREA]})
        area = popolo.areas[0]
        assert area.wikidata == 'Q3032626'

    def test_area_repr(self):
        popolo = Popolo({"areas": [EXAMPLE_AREA]})
        area = popolo.areas[0]
        if six.PY2:
            assert repr(area) == b"<Area: Tartu linn>"
        else:
            assert repr(area) == u"<Area: Tartu linn>"

    def test_area_identity_equality_and_inequality(self):
        popolo_a = Popolo({"areas": [EXAMPLE_AREA]})
        area_a = popolo_a.areas[0]
        popolo_b = Popolo({"areas": [EXAMPLE_AREA]})
        area_b = popolo_b.areas[0]
        assert area_a == area_b
        assert not (area_a != area_b)
