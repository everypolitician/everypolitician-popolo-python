
from datetime import date
from approx_dates.models import ApproxDate
from .funcs import first
import six

class Attribute(object):
    '''
    Exposes raw json values for getting and setting
    
    Works in conjecture with PopoloObject
    
    so:
    
    id = Attribute()
    
    will give a PopoloObject with an id attribute that gets and
    sets the 'id' attr of self.data.
    
    id = Attribute(default="16")
    
    Sets a default extraction value of 16.
    
    id = Attribute(null=True)
    
    will return None rather than an error if the value is absent.
    
    '''
    def __init__(self,attr="",default=None,null=False,allow_multiple=False):
        self.attr = attr
        self.default_value = default
        self.allow_null_default = null
        self.allow_multiple = allow_multiple

    def __get__(self, obj, type=None):
        if self.allow_null_default == False and self.default_value == None:
            return obj.data.get(self.attr)
        else:
            return obj.data.get(self.attr,self.default_value)

    def __set__(self,obj,value):
        obj.data[self.attr] = value

class RelatedAttribute(Attribute):
    """
    returns 'related' objects - e.g. if person_id = 5, returns Person 5
    """
    def __init__(self,attr="",default=None,null=False,
                 id_attr=None,collection=None):
        self.attr = attr
        self.default_value = default
        self.allow_null_default = null
        self._id_attr = id_attr
        self._collection = collection
            
    @property
    def id_attr(self):
        if self._id_attr:
            return self._id_attr
        else:
            return self.attr + "_id"
          
    @property  
    def collection(self):
        if self._collection:
            return self._collection
        else:
            return self.attr + "s"   
         
    def __get__(self, obj, type=None):
        collection = getattr(obj.all_popolo,self.collection)
        return collection.lookup_from_key[getattr(obj,self.id_attr)]
    
    def __set__(self,obj,value):
        setattr(obj,self.id_attr,value.id)

class DateAttribute(Attribute):
    """
    Interacts with ApproxDates - sets iso, retrieves ApproxDate
    """
    def __get__(self, obj, type=None):
        if self.allow_null_default:
            return obj.get_date(self.attr,None)
        else:
            return obj.get_date(self.attr,self.default_value)
    
    def __set__(self,obj,value):
        if isinstance(value,ApproxDate):
            obj.data[self.attr] = value.isoformat()
        else:
            obj.data[self.attr] = value


class IdentiferAttribute(Attribute):
    """
    For getting and setting values deeper in linked data.
    """
    getter = "identifier_values"
    
    def __get__(self, obj, type=None):
        getter = getattr(obj,self.__class__.getter)
        v = getter(self.attr)
        if v:
            if self.allow_multiple:
                return v
            else:
                return first(v)
        elif v == None and self.allow_null_default:
            return None
        else:
            return self.default_value
        
    def __set__(self,obj,value):
        setter = getattr(obj,"set_" + self.__class__.getter)
        setter(self.attr,value)

class LinkAttribute(IdentiferAttribute):
    getter = "link_values"
    
class ContactAttribute(IdentiferAttribute):
    getter = "contact_detail_values"

class PopoloMeta(type):
    
    def __new__(cls, name, parents, dct):
        
        """
        If attr value not specified for an attribute, gives it the name assigned
        
        so 
        
        name = Attribute()
        
        is equivalent to:
        
        name = Attribute(attr="name")
        """
        
        for k,v in six.iteritems(dct):
            if isinstance(v,Attribute) :
                if v.attr == "":
                    v.attr = k 

        cls = super(PopoloMeta, cls).__new__(cls, name, parents, dct)
        return cls
 

class PopoloObject(six.with_metaclass(PopoloMeta,object)):

    class DoesNotExist(Exception):
        pass

    class MultipleObjectsReturned(Exception):
        pass

    def __init__(self, data=None, all_popolo=None,**kwargs):
        if data == None:
            data = {}
        data.update(kwargs)
        self.data = data
        self.all_popolo = all_popolo

    def get_date(self, attr, default):
        d = self.data.get(attr)
        if d:
            return ApproxDate.from_iso8601(d)
        return default

    def get_related_object_list(self, popolo_array):
        return self.data.get(popolo_array, [])

    def get_related_values(
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
        return [
            o[info_value_key]
            for o in self.get_related_object_list(popolo_array)
            if o[info_type_key] == info_type
            ]

    def del_related_values(self,popolo_array, info_type_key, info_type):
        obj_list = self.get_related_object_list(popolo_array)
        if obj_list:
            for x,o in enumerate(obj_list):
                if o[info_type_key] == info_type:
                    break
            
            if obj_list[x][info_type_key] == info_type:
                del obj_list[x]
            

    def set_related_values(self, popolo_array
                           , info_type_key, info_type, info_value_key,new_value):
        """
        allows related values to be set
        """
        
        obj_list = self.get_related_object_list(popolo_array)
        for o in obj_list:
            if o[info_type_key] == info_type:
                o[info_value_key] = new_value
                return
        new = {info_type_key:info_type,
               info_value_key:new_value}
        obj_list.append(new)
        self.data[popolo_array] = obj_list

    def identifier_values(self, scheme):
        return self.get_related_values(
            'identifiers', 'scheme', scheme, 'identifier')

    def set_identifier_values(self, scheme,value):
        """
        set an identifer value
        """
        self.set_related_values(
            'identifiers', 'scheme', scheme, 'identifier',value)

    def identifier_value(self, scheme):
        return first(self.identifier_values(scheme))

    def link_values(self, note):
        return self.get_related_values('links', 'note', note, 'url')

    def set_link_values(self, note,value):
        """
        set a link value
        """
        self.set_related_values('links', 'note', note, 'url',value)

    def del_link_values(self, note):
        """
        set a link value
        """
        self.del_related_values('links', 'note', note)


    def link_value(self, note):
        return first(self.link_values(note))

    def contact_detail_values(self, contact_type):
        return self.get_related_values(
            'contact_details', 'type', contact_type, 'value')

    def del_contact_detail_values(self, contact_type):
        return self.del_contact_detail_values(
            'contact_details', 'type', contact_type)
    
    def set_contact_detail_values(self, contact_type,new_value):
        return self.set_related_values(
            'contact_details', 'type', contact_type, 'value',new_value)

    def contact_detail_value(self, contact_type):
        return first(self.contact_detail_values(contact_type))

    @property
    def key_for_hash(self):
        return self.id

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.id != other.id
        return NotImplemented

    def __hash__(self):
        return hash(self.key_for_hash)

    def repr_helper(self, enclosed_text):
        fmt = str('<{0}: {1}>')
        class_name = type(self).__name__
        if six.PY2:
            return fmt.format(class_name, enclosed_text.encode('utf-8'))
        return fmt.format(class_name, enclosed_text)

    def __repr__(self):
        preferred_order = ["name","label","id"]
        for o in preferred_order:
            if hasattr(self,o):
                return self.repr_helper(getattr(self,o))


class CurrentMixin(object):

    def current_at(self, when):
        return ApproxDate.possibly_between(
            self.start_date, when, self.end_date)

    @property
    def current(self):
        return self.current_at(date.today())

