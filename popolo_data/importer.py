import json

import requests

from .base import (
    AreaCollection, EventCollection, MembershipCollection, PersonCollection,
    OrganizationCollection, PostCollection)


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
        return PersonCollection(self.json_data.get('persons', []), self)

    @property
    def organizations(self):
        return OrganizationCollection(
            self.json_data.get('organizations', []), self)

    @property
    def memberships(self):
        return MembershipCollection(
            self.json_data.get('memberships', []), self)

    @property
    def areas(self):
        return AreaCollection(self.json_data.get('areas', []), self)

    @property
    def posts(self):
        return PostCollection(self.json_data.get('posts', []), self)

    @property
    def events(self):
        return EventCollection(self.json_data.get('events', []), self)

    @property
    def elections(self):
        return self.events.elections

    @property
    def legislative_periods(self):
        return self.events.legislative_periods

    @property
    def terms(self):
        return self.legislative_periods

    @property
    def latest_legislative_period(self):
        lps = self.legislative_periods
        return max(lps, key=lambda lp: lp.start_date.midpoint_date)

    @property
    def latest_term(self):
        return self.latest_legislative_period
