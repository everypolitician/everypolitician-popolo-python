'''
Created on Dec 19, 2016

@author: Alex
'''
from six.moves.urllib_parse import urlsplit
import json
import re

def _is_name_current_at(name_object, date_string):
    start_range = name_object.get('start_date') or '0001-01-01'
    end_range = name_object.get('end_date') or '9999-12-31'
    return date_string >= start_range and date_string <= end_range

def extract_twitter_username(username_or_url):
    split_url = urlsplit(username_or_url)
    if split_url.netloc == 'twitter.com':
        return re.sub(r'^/([^/]+).*', r'\1', split_url.path)
    return username_or_url.strip().lstrip('@')

def first(l):
    '''Return the first item of a list, or None if it's empty'''
    return l[0] if l else None

def unique_preserving_order(sequence):
    '''Return a list with only the unique elements, preserving order

    This is from http://stackoverflow.com/a/480227/223092'''
    seen = set()
    seen_add = seen.add
    return [x for x in sequence if not (x in seen or seen_add(x))]

