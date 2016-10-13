from mock import patch, Mock
from unittest import TestCase

import pytest
from six import text_type

from .helpers import example_file

from popolo_data.importer import Popolo


class TestLoading(TestCase):

    def test_can_create_from_a_filename(self):
        with example_file(b'{}') as filename:
            Popolo.from_filename(filename)

    def test_fails_to_create_from_a_nonexistent_filename(self):
        with pytest.raises(IOError) as excinfo:
            Popolo.from_filename('non-existent-file.json')
        assert 'No such file or directory' in text_type(excinfo)

    @patch('popolo_data.importer.requests.get')
    def test_create_from_url(self, faked_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'persons': [{'name': 'Joe Bloggs'}]
        }
        faked_get.side_effect = lambda url: mock_response
        popolo = Popolo.from_url('http://example.org/popolo.json')
        assert popolo.persons.first.name == 'Joe Bloggs'
