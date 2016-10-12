import json

from .base import (
    MembershipCollection, PersonCollection, OrganizationCollection)


class Popolo(object):

    def __init__(self, filename):
        with open(filename) as f:
            self.json_data = json.load(f)

    @property
    def persons(self):
        return PersonCollection(self.json_data.get('persons', []))

    @property
    def organizations(self):
        return OrganizationCollection(self.json_data.get('organizations', []))

    @property
    def memberships(self):
        return MembershipCollection(self.json_data.get('memberships', []))
