'''

'''

from popolo_data.models import Person, Organization, Membership, Event, Area, Post
from .funcs import first

class PopoloCollection(object):

    object_class = None

    def __init__(self, data_list, all_popolo):
        """
        converts json objects to class
        """
        self.object_class = self.__class__.object_class
        self.all_popolo = all_popolo
        self.object_list = \
            [self.object_class(data, all_popolo) for data in data_list]
        self.lookup_from_key = {}
        for o in self.object_list:
            self.lookup_from_key[o.key_for_hash] = o

    def __len__(self):
        return len(self.object_list)

    def raw_data(self):
        return [x.data for x in self.object_list]

    def __getitem__(self, index):
        return self.object_list[index]

    @property
    def first(self):
        return first(self.object_list)

    def filter(self, **kwargs):
        return [
            o for o in self.object_list
            if all(getattr(o, k) == v for k, v in kwargs.items())
        ]

    def append(self,new):
        new.all_popolo = self.all_popolo
        self.lookup_from_key[new.key_for_hash] = new
        self.object_list.append(new)
        
    add = append

    def get(self, **kwargs):
        matches = self.filter(**kwargs)
        n = len(matches)
        if n == 0:
            msg = "No {0} found matching {1}"
            raise self.object_class.DoesNotExist(msg.format(
                self.object_class, kwargs))
        elif n > 1:
            msg = "Multiple {0} objects ({1}) found matching {2}"
            raise self.object_class.MultipleObjectsReturned(msg.format(
                self.object_class, n, kwargs))
        return matches[0]


class PersonCollection(PopoloCollection):
    object_class = Person

class OrganizationCollection(PopoloCollection):
    object_class = Organization

class MembershipCollection(PopoloCollection):
    object_class = Membership

class AreaCollection(PopoloCollection):
    object_class = Area

class PostCollection(PopoloCollection):
    object_class = Post

class EventCollection(PopoloCollection):
    object_class = Event
