from datetime import date, datetime

import six


class ObjectDoesNotExist(Exception):
    pass


class MultipleObjectsReturned(Exception):
    pass


def _is_name_current_at(name_object, date_string):
    start_range = name_object.get('start_date') or '0001-01-01'
    end_range = name_object.get('end_date') or '9999-12-31'
    return date_string >= start_range and date_string <= end_range


class PopoloObject(object):

    def __init__(self, data, all_popolo):
        self.data = data
        self.all_popolo = all_popolo

    def get_date(self, attr, default):
        d = self.data.get(attr)
        if d:
            return datetime.strptime(d, '%Y-%m-%d').date()
        return default

    def get_related_object_list(self, popolo_array):
        return self.data.get(popolo_array, [])

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
            o[info_value_key]
            for o in self.get_related_object_list(popolo_array)
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
    def family_name(self):
        return self.data.get('family_name')

    @property
    def given_name(self):
        return self.data.get('given_name')

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

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return NotImplemented

    def name_at(self, particular_date):
        historic_names = [n for n in self.other_names if n.get('end_date')]
        if not historic_names:
            return self.name
        names_at_date = [
            n for n in historic_names
            if _is_name_current_at(n, str(particular_date))
        ]
        if not names_at_date:
            return self.name
        if len(names_at_date) > 1:
            msg = "Multiple names for {0} found at date {1}"
            raise Exception(msg.format(self, particular_date))
        return names_at_date[0]['name']

    @property
    def links(self):
        return self.get_related_object_list('links')

    @property
    def contact_details(self):
        return self.get_related_object_list('contact_details')

    @property
    def identifiers(self):
        return self.get_related_object_list('identifiers')

    @property
    def images(self):
        return self.get_related_object_list('images')

    @property
    def other_names(self):
        return self.get_related_object_list('other_names')

    @property
    def sources(self):
        return self.get_related_object_list('sources')

    @property
    def memberships(self):
        return [
            m for m in self.all_popolo.memberships
            if m.person_id == self.id
        ]

class Organization(PopoloObject):

    class DoesNotExist(ObjectDoesNotExist):
        pass

    class MultipleObjectsReturned(MultipleObjectsReturned):
        pass

    @property
    def id(self):
        return self.data.get('id')

    @property
    def name(self):
        return self.data.get('name')

    @property
    def wikidata(self):
        return self.identifier('wikidata')

    @property
    def classification(self):
        return self.data.get('classification')

    @property
    def image(self):
        return self.data.get('image')

    @property
    def founding_date(self):
        return self.get_date('founding_date', None)

    @property
    def dissolution_date(self):
        return self.get_date('dissolution_date', None)

    @property
    def seats(self):
        return self.data.get('seats')

    @property
    def other_names(self):
        return self.data.get('other_names', [])

    def __repr__(self):
        fmt = str('<Organization: {0}>')
        if six.PY2:
            return fmt.format(self.name.encode('utf-8'))
        return fmt.format(self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return NotImplemented

    @property
    def identifiers(self):
        return self.get_related_object_list('identifiers')

    @property
    def links(self):
        return self.get_related_object_list('links')


class Membership(PopoloObject):

    class DoesNotExist(ObjectDoesNotExist):
        pass

    class MultipleObjectsReturned(MultipleObjectsReturned):
        pass

    @property
    def role(self):
        return self.data.get('role')

    @property
    def person_id(self):
        return self.data.get('person_id')

    @property
    def person(self):
        return self.all_popolo.persons.get(id=self.person_id)

    @property
    def organization_id(self):
        return self.data.get('organization_id')

    @property
    def organization(self):
        return self.all_popolo.organizations.get(id=self.organization_id)

    @property
    def area_id(self):
        return self.data.get('area_id')

    @property
    def area(self):
        return self.all_popolo.areas.get(id=self.area_id)

    @property
    def legislative_period_id(self):
        return self.data.get('legislative_period_id')

    @property
    def legislative_period(self):
        return self.all_popolo.events.get(id=self.legislative_period_id)

    @property
    def on_behalf_of_id(self):
        return self.data.get('on_behalf_of_id')

    @property
    def on_behalf_of(self):
        return self.all_popolo.organizations.get(id=self.on_behalf_of_id)

    @property
    def post_id(self):
        return self.data.get('post_id')

    @property
    def post(self):
        return self.all_popolo.posts.get(id=self.post_id)

    @property
    def start_date(self):
        return self.get_date('start_date', date(1, 1, 1))

    @property
    def end_date(self):
        return self.get_date('end_date', date(9999, 12, 31))

    def __repr__(self):
        fmt = str("<Membership: '{0}' at '{1}'>")
        return fmt.format(self.person_id, self.organization_id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.data == other.data
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.data != other.data
        return NotImplemented


class Area(PopoloObject):

    @property
    def id(self):
        return self.data.get('id')

    @property
    def name(self):
        return self.data.get('name')

    @property
    def type(self):
        return self.data.get('type')

    @property
    def identifiers(self):
        return self.get_related_object_list('identifiers')

    @property
    def other_names(self):
        return self.get_related_object_list('other_names')

    @property
    def wikidata(self):
        return self.identifier('wikidata')

    def __repr__(self):
        fmt = str("<Area: {0}>")
        return fmt.format(self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return NotImplemented


class Post(PopoloObject):

    @property
    def id(self):
        return self.data.get('id')

    @property
    def label(self):
        return self.data.get('label')

    @property
    def organization_id(self):
        return self.data.get('organization_id')

    @property
    def organization(self):
        return self.all_popolo.organizations.get(id=self.organization_id)

    def __repr__(self):
        fmt = str("<Post: {0}>")
        return fmt.format(self.label)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return NotImplemented


class Event(PopoloObject):

    @property
    def id(self):
        return self.data.get('id')

    @property
    def name(self):
        return self.data.get('name')

    @property
    def classification(self):
        return self.data.get('classification')

    @property
    def start_date(self):
        return self.get_date('start_date', date(1, 1, 1))

    @property
    def end_date(self):
        return self.get_date('end_date', date(9999, 12, 31))

    @property
    def organization_id(self):
        return self.data.get('organization_id')

    @property
    def organization(self):
        return self.all_popolo.organizations.get(id=self.organization_id)

    def __repr__(self):
        fmt = str("<Event: {0}>")
        return fmt.format(self.name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return NotImplemented

    @property
    def identifiers(self):
        return self.get_related_object_list('identifiers')


class PopoloCollection(object):

    def __init__(self, data_list, object_class, all_popolo):
        self.object_class = object_class
        self.object_list = \
            [self.object_class(data, all_popolo) for data in data_list]

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

    def __init__(self, persons_data, all_popolo):
        super(PersonCollection, self).__init__(
            persons_data, Person, all_popolo)


class OrganizationCollection(PopoloCollection):

    def __init__(self, organizations_data, all_popolo):
        super(OrganizationCollection, self).__init__(
            organizations_data, Organization, all_popolo)


class MembershipCollection(PopoloCollection):

    def __init__(self, memberships_data, all_popolo):
        super(MembershipCollection, self).__init__(
            memberships_data, Membership, all_popolo)


class AreaCollection(PopoloCollection):

    def __init__(self, areas_data, all_popolo):
        super(AreaCollection, self).__init__(
            areas_data, Area, all_popolo)


class PostCollection(PopoloCollection):

    def __init__(self, posts_data, all_popolo):
        super(PostCollection, self).__init__(
            posts_data, Post, all_popolo)


class EventCollection(PopoloCollection):

    def __init__(self, events_data, all_popolo):
        super(EventCollection, self).__init__(
            events_data, Event, all_popolo)
