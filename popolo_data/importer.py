import json

import requests

from .base import (
    MembershipCollection, PersonCollection, OrganizationCollection)


class Popolo(object):

    @classmethod
    def from_filename(cls, filename):
        with open(filename) as f:
            return cls(json.load(f))

    @classmethod
    def from_url(cls, url):
        r = requests.get(url)
        return cls(r.json())

    def __init__(self, json_data):
        self.json_data = json_data

    @property
    def persons(self):
        return PersonCollection(self.json_data.get('persons', []))

    @property
    def organizations(self):
        return OrganizationCollection(self.json_data.get('organizations', []))

    @property
    def memberships(self):
        return MembershipCollection(self.json_data.get('memberships', []))
