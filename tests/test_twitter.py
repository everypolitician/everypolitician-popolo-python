from __future__ import unicode_literals

from unittest import TestCase

from popolo_data.base import extract_twitter_username


class TestNormalizingTwitterUsernames(TestCase):

    def test_strip_whitespace(self):
        result = extract_twitter_username('  everypolitbot  ')
        assert result == 'everypolitbot'

    def test_remove_extraneous_at_prefix(self):
        result = extract_twitter_username('@everypolitbot')
        assert result == 'everypolitbot'

    def test_extract_username_from_twitter_url(self):
        result = extract_twitter_username('https://twitter.com/everypolitbot')
        assert result == 'everypolitbot'

    def test_extract_username_from_twitter_url_with_trailing_slash(self):
        result = extract_twitter_username('https://twitter.com/everypolitbot/')
        assert result == 'everypolitbot'
