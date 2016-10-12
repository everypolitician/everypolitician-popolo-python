from datetime import date, datetime

import six


class ObjectDoesNotExist(Exception):
    pass


class MultipleObjectsReturned(Exception):
    pass


class PopoloObject(object):

    def __init__(self, data):
        self.data = data

    def get_date(self, attr, default):
        d = self.data.get(attr)
        if d:
            return datetime.strptime(d, '%Y-%m-%d').date()
        return default

    def identifier(self, scheme):
        matches = [
            i['identifier'] for i in self.data.get('identifiers', [])
            if i['scheme'] == scheme]
        n = len(matches)
        if n == 0:
            return None
        elif n > 1:
            msg = "More than one identifier found with scheme {0}; " \
                "there were {1}"
            raise MultipleObjectsReturned(msg.format(scheme, n))
        return matches[0]


class Person(PopoloObject):

    class DoesNotExist(ObjectDoesNotExist):
        pass

    class MultipleObjectsReturned(MultipleObjectsReturned):
        pass

    @property
    def id(self):
        return self.data.get('id')

    @property
    def image(self):
        return self.data.get('image')

    @property
    def name(self):
        return self.data.get('name')

    @property
    def national_identity(self):
        return self.data.get('national_identity')

    @property
    def wikidata(self):
        return self.identifier('wikidata')

    def __repr__(self):
        fmt = str('<Person: {0}>')
        if six.PY2:
            return fmt.format(self.name.encode('utf-8'))
        return fmt.format(self.name)


class Organization(PopoloObject):

    class DoesNotExist(ObjectDoesNotExist):
        pass

    class MultipleObjectsReturned(MultipleObjectsReturned):
        pass

    @property
    def name(self):
        return self.data.get('name')

    @property
    def wikidata(self):
        return self.identifier('wikidata')

    @property
    def classification(self):
        return self.data.get('classification')

    def __repr__(self):
        fmt = str('<Organization: {0}>')
        if six.PY2:
            return fmt.format(self.name.encode('utf-8'))
        return fmt.format(self.name)


class Membership(PopoloObject):

    class DoesNotExist(ObjectDoesNotExist):
        pass

    class MultipleObjectsReturned(MultipleObjectsReturned):
        pass

    @property
    def start_date(self):
        return self.get_date('start_date', date(1, 1, 1))

    @property
    def end_date(self):
        return self.get_date('end_date', date(9999, 12, 31))


class PopoloCollection(object):

    def __init__(self, data_list, object_class):
        self.object_class = object_class
        self.object_list = \
            [self.object_class(data) for data in data_list]

    def __len__(self):
        return len(self.object_list)

    def __getitem__(self, index):
        return self.object_list[index]

    @property
    def first(self):
        if len(self.object_list):
            return self[0]
        return None

    def filter(self, **kwargs):
        return [
            o for o in self.object_list
            if all(getattr(o, k) == v for k, v in kwargs.items())
        ]

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

    def __init__(self, persons_data):
        super(PersonCollection, self).__init__(
            persons_data, Person)


class OrganizationCollection(PopoloCollection):

    def __init__(self, organizations_data):
        super(OrganizationCollection, self).__init__(
            organizations_data, Organization)


class MembershipCollection(PopoloCollection):

    def __init__(self, memberships_data):
        super(MembershipCollection, self).__init__(
            memberships_data, Membership)
