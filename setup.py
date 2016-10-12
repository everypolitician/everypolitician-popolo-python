from setuptools import setup, find_packages
setup(
    name = "everypolitician-popolo",
    version = "0.0.1",
    packages = find_packages(),
    author = "Mark Longair",
    author_email = "mark@mysociety.org",
    description = "Parse and model Popolo data from EveryPolitician",
    license = "AGPL",
    keywords = "politics data civic-tech",
    install_requires = [
        'requests',
        'six >= 1.9.0',
    ]
)
