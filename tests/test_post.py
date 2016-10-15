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
