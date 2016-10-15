# -*- coding: utf-8 -*-

from unittest import TestCase

import six

from .helpers import example_file

from popolo_data.importer import Popolo


EXAMPLE_POST_JSON = b'''
{
    "posts": [
        {
            "id": "nominated_representative",
            "label": "Nominated Representative",
            "organization_id": "574eff8e-8171-4f2b-8279-60ed8dec1a2a"
        },
        {
            "id": "women's_representative",
            "label": "Women's Representative",
            "organization_id": "574eff8e-8171-4f2b-8279-60ed8dec1a2a"
        }
    ],
    "organizations": [
        {
            "classification": "legislature",
            "id": "574eff8e-8171-4f2b-8279-60ed8dec1a2a",
            "identifiers": [
                {
                    "identifier": "Q1701225",
                    "scheme": "wikidata"
                }
            ],
            "name": "National Assembly",
            "seats": 349
        }
    ]
}
'''

class TestPosts(TestCase):

    def test_empty_file_gives_no_posts(self):
        popolo = Popolo({})
        assert len(popolo.posts) == 0

    def test_single_post_with_label(self):
        with example_file(EXAMPLE_POST_JSON) as fname:
            popolo = Popolo.from_filename(fname)
            assert len(popolo.posts) == 2
            post = popolo.posts[0]
            assert post.label == 'Nominated Representative'

    def test_post_id(self):
        with example_file(EXAMPLE_POST_JSON) as fname:
            popolo = Popolo.from_filename(fname)
            post = popolo.posts.first
            assert post.id == 'nominated_representative'

    def test_post_has_organization_id(self):
        with example_file(EXAMPLE_POST_JSON) as fname:
            popolo = Popolo.from_filename(fname)
            assert len(popolo.posts) == 2
            post = popolo.posts[0]
            assert post.organization_id == '574eff8e-8171-4f2b-8279-60ed8dec1a2a'

    def test_post_has_organization(self):
        with example_file(EXAMPLE_POST_JSON) as fname:
            popolo = Popolo.from_filename(fname)
            national_assembly = popolo.organizations.first
            nom_rep = popolo.posts.first
            assert nom_rep.organization == national_assembly

    def test_area_repr(self):
        with example_file(EXAMPLE_POST_JSON) as fname:
            popolo = Popolo.from_filename(fname)
            post = popolo.posts.first
            if six.PY2:
                assert repr(post) == b"<Post: Nominated Representative>"
            else:
                assert repr(post) == u"<Post: Nominated Representative>"

    def test_post_identity_equality_and_inequality(self):
        with example_file(EXAMPLE_POST_JSON) as fname:
            popolo_a = Popolo.from_filename(fname)
        post_a = popolo_a.posts.first
        with example_file(EXAMPLE_POST_JSON) as fname:
            popolo_b = Popolo.from_filename(fname)
        post_b = popolo_b.posts.first
        assert post_a == post_b
        assert not (post_a != post_b)
