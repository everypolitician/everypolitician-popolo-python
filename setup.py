from setuptools import setup, find_packages
from os.path import join, dirname

with open(join(dirname(__file__), 'README.rst')) as f:
    readme_text = f.read()

setup(
    name = "everypolitician-popolo",
    version = "0.0.4",
    packages = find_packages(),
    author = "Mark Longair",
    author_email = "mark@mysociety.org",
    description = "Parse and model Popolo data from EveryPolitician",
    long_description = readme_text,
    license = "AGPL",
    keywords = "politics data civic-tech",
    install_requires = [
        'requests',
        'six >= 1.9.0',
    ]
)
