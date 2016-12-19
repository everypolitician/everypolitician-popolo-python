"""
import export functions
"""


import json
import requests
import io

from .collections import (
    PopoloCollection, AreaCollection, EventCollection, MembershipCollection, PersonCollection,
    OrganizationCollection, PostCollection)

class NotAValidType(TypeError):
    pass

class Popolo(object):

    @classmethod
    def from_filename(cls, filename):
        with open(filename) as f:
            return cls(json.load(f))

    @classmethod
    def from_url(cls, url):
        r = requests.get(url)
        return cls(r.json())

    @classmethod
    def new(cls):
        return cls({})

    def __init__(self, json_data=None):
        if json_data == None:
            json_data = {}
        self.json_data = json_data
        json_get = self.json_data.get
        self.persons = PersonCollection(json_get('persons', []), self)
        self.organizations = OrganizationCollection(json_get('organizations', []), self)
        self.memberships =  MembershipCollection(json_get('memberships', []), self)
        self.areas = AreaCollection(json_get('areas', []), self)
        self.posts = PostCollection(json_get('posts', []), self)
        self.events = EventCollection(json_get('events', []), self)
    
    @property
    def collections(self):
        return [[k,v] for k,v in self.__dict__.iteritems()\
                if isinstance(v,PopoloCollection)]

    def add(self,new):
        """
        find the correct collection for the object and add it
        """
        if isinstance(new,list):
            ll = new
        else:
            ll = [new]
        
        to_return = []
        for l in ll:
            for k,collection in self.collections:
                if isinstance(l,collection.object_class):
                    to_return.append(collection.add(l))
                    break
        
        if len(to_return) != len(ll):
            raise NotAValidType("This type can't be used with Popolo.")

    def to_filename(self,filename):
        di = {k:v.raw_data() for k,v in self.collections}
        with open(filename,"wb") as f:
            json.dump(di,f,indent=4, sort_keys=True, ensure_ascii=False)
        
    def to_json(self):
        di = {k:v.raw_data() for k,v in self.collections}
        return json.dumps(di,indent=4, sort_keys=True , ensure_ascii=False)        
