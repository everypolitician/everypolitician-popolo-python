from __future__ import unicode_literals

from contextlib import contextmanager
import os
from tempfile import NamedTemporaryFile


@contextmanager
def example_file(json_for_file):
    ntf = NamedTemporaryFile(delete=False)
    try:
        ntf.write(json_for_file)
        ntf.close()
        yield ntf.name
    finally:
        os.remove(ntf.name)
