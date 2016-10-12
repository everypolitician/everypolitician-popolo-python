from unittest import TestCase

import pytest
from six import text_type

from .helpers import example_file

from popolo_data.importer import Popolo


class TestLoading(TestCase):

    def test_can_create_from_a_filename(self):
        with example_file(b'{}') as filename:
            Popolo(filename)

    def test_fails_to_create_from_a_nonexistent_filename(self):
        with pytest.raises(IOError) as excinfo:
            Popolo('non-existent-file.json')
        assert 'No such file or directory' in text_type(excinfo)
