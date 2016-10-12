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

    def get_related_value(
            self, popolo_array, info_type_key, info_type, info_value_key):
        '''Get a value from one of the Popolo related objects

        For example, if you have a person with related links, like
        this:

            {
                "name": "Dale Cooper",
                "links": [
                    {
                        "note": "wikipedia",
                        "url": "https://en.wikipedia.org/wiki/Dale_Cooper"
                    }
                ]
            }

        When calling this method to get the Wikipedia URL, you would use:

            popolo_array='links'
            info_type_key='note'
            info_type='wikipedia'
            info_value_key='url'

        ... so the following would work:

            self.get_related_value('links', 'note', 'wikipedia', 'url')
            # => 'https://en.wikipedia.org/wiki/Dale_Cooper'
        '''
        matches = [
            o[info_value_key] for o in self.data.get(popolo_array, [])
            if o[info_type_key] == info_type]
        n = len(matches)
        if n == 0:
            return None
        elif n > 1:
            msg = "Multiple {0} found with {1}: {2}; there were {3}"
            raise MultipleObjectsReturned(msg.format(
                popolo_array, info_type_key, info_type, n))
        return matches[0]

    def identifier(self, scheme):
        return self.get_related_value(
            'identifiers', 'scheme', scheme, 'identifier')

    def link(self, note):
        return self.get_related_value('links', 'note', note, 'url')

    def contact_detail(self, contact_type):
        return self.get_related_value(
            'contact_details', 'type', contact_type, 'value')


class Person(PopoloObject):

    class DoesNotExist(ObjectDoesNotExist):
        pass

    class MultipleObjectsReturned(MultipleObjectsReturned):
        pass

    @property
    def id(self):
        return self.data.get('id')

    @property
    def email(self):
        return self.data.get('email')

    @property
    def gender(self):
        return self.data.get('gender')

    @property
    def honorific_prefix(self):
        return self.data.get('honorific_prefix')

    @property
    def honorific_suffix(self):
        return self.data.get('honorific_suffix')

    @property
    def image(self):
        return self.data.get('image')

    @property
    def name(self):
        return self.data.get('name')

    @property
    def sort_name(self):
        return self.data.get('sort_name')

    @property
    def national_identity(self):
        return self.data.get('national_identity')

    @property
    def summary(self):
        return self.data.get('summary')

    @property
    def biography(self):
        return self.data.get('biography')

    @property
    def birth_date(self):
        return self.get_date('birth_date', None)

    @property
    def death_date(self):
        return self.get_date('death_date', None)

    @property
    def wikidata(self):
        return self.identifier('wikidata')

    @property
    def twitter(self):
        return self.contact_detail('twitter') or self.link('twitter')

    @property
    def phone(self):
        return self.contact_detail('phone')

    @property
    def facebook(self):
        return self.link('facebook')

    @property
    def fax(self):
        return self.contact_detail('fax')

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
