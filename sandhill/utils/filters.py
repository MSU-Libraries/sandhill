"""Filters for jinja templating engine"""
import urllib
import validators
import os
from ast import literal_eval
import mimetypes
from sandhill import app
from sandhill.utils.generic import ifnone
from datetime import datetime
from jinja2 import contextfilter, TemplateError
from collections.abc import Hashable
import copy

@app.template_filter()
def size_format(value):
    """ Jinja filter to format the size """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    nbytes = int(value) if f"{value}".isdigit() else 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024
        i += 1
    f = ('%.1f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

@app.template_filter()
def is_list(value):
    """ Check if a value is a list """
    return isinstance(value, list)

@app.template_filter()
def get_extension(value):
    """Take in mimetype and return extension."""
    mimetypes.add_type("audio/wav", '.wav')
    extension = None
    preferred = [".txt", ".jpg", ".mp3"]
    all_extensions = mimetypes.guess_all_extensions(value)
    if all_extensions:
        for ext in all_extensions:
            if ext in preferred:
                extension = ext
                break
        if not extension:
            extension = all_extensions[0]
    else:
        extension = ".???"
    return extension.upper()[1:]

@app.template_filter()
def head(value):
    """If value is a non-empty list, returns the head of the list, otherwise return the value as is"""
    if isinstance(value, list) and value:
        value = value[0]
    return value

@app.template_filter('solr_escape')
def solr_escape(value):
    """Filter to escape a value being passed to Solr
    args:
        value (str): string to escape Solr characters
    returns:
        (str): same string but with Solr characters escaped
    """
    if isinstance(value, str):
        escapes = { ' ': r'\ ', '+': r'\+', '-': r'\-', '&': r'\&', '|': r'\|', '!': r'\!',
                    '(': r'\(', ')': r'\)', '{': r'\{', '}': r'\}', '[': r'\[', ']': r'\]',
                    '^': r'\^', '~': r'\~', '*': r'\*', '?': r'\?', ':': r'\:', '"': r'\"',
                    ';': r'\;' }
        value = value.replace('\\', r'\\')  # must be first replacement
        for k, v in escapes.items():
            value = value.replace(k, v)
    return value

@app.template_filter('solr_decode')
def solr_decode(value):
    """Filter to decode a value previously encoded for Solr
    args:
        value (str): string with Solr escapes to be decoded
    returns:
        (str): same string after being decoded
    """
    if isinstance(value, str):
        escapes = { ' ': r'\ ', '+': r'\+', '-': r'\-', '&': r'\&', '|': r'\|', '!': r'\!',
                    '(': r'\(', ')': r'\)', '{': r'\{', '}': r'\}', '[': r'\[', ']': r'\]',
                    '^': r'\^', '~': r'\~', '*': r'\*', '?': r'\?', ':': r'\:', '"': r'\"',
                    ';': r'\;' }
        for k, v in escapes.items():
            value = value.replace(v, k)
        value = value.replace(r'\\', '\\')  # must be last replacement
    return value

@app.template_filter('set_child_key')
def set_child_key(parent_dict, parent_key, key, value):
    """Take dictionary of url components, and update 'key' with 'value'.
    args:
        parent_dict (dict): dictionary to add parent_key to
        parent_key (str|int|other hashable type): parent key to add to the parent_dict
        key (str|int|other hashable type): key to put under parent_key
        value (any): value to give that key
    returns:
        parent_dict (dict): The updated parent dictionary
    """
    if isinstance(parent_dict, dict) and isinstance(parent_key, Hashable) and isinstance(key, Hashable):
        if parent_key not in parent_dict:
            parent_dict[parent_key] = {}
        parent_dict[parent_key][key] = value
    return parent_dict

@app.template_filter('assemble_url')
def assemble_url(url_components):
    """Take url_components (derived from Flask Request object) and returns a url.
    args:
        url_components (dict): components of the URL to build
    returns:
        (str): fully combined URL with query arguments
    """
    url = ""
    if isinstance(url_components, dict) and "path" in url_components:
        url = url_components["path"]
        if "query_args" in url_components and isinstance(url_components['query_args'], dict) and url_components['query_args']:
            url = url + "?" + urllib.parse.urlencode(url_components["query_args"], doseq=True)
    return url

@app.template_filter('date_passed')
def date_passed(value):
    """ Checks if the embargoded date is greater than the current date
    args:
        value (str): Date in the format yyy-mm-dd that needs to be checked
    returns:
        (bool): If the given date is less than the current date or not
    """
    try:
        value_date =  datetime.strptime(value, "%Y-%m-%d")
        current_date  = datetime.now()
        if value_date.date() < current_date.date():
            return True
    except (ValueError, TypeError) as err:
        app.logger.error(f"Unable to get a valid date in {value}. Error {err} ")
    return False

@app.template_filter('render')
@contextfilter
def render(context, value):
    """Renders a given string or literal
    args:
        context (Jinja2 context): context information and variables to use when
            evaluating the provided template string.
        value (str): Jinja2 template string to evaluate given the provided context
    returns:
        (str|None): the rendered value or string
    """
    data_val = None

    try:
        data_template = context.environment.from_string(value)
        data_val = data_template.render(**context)
    except TemplateError as terr:
        app.logger.error(f"Invalid template provided: {value}. Error: {terr}")

    return data_val

@app.template_filter('render_literal')
@contextfilter
def render_literal(context, value, fallback_to_str=True):
    """Renders a Jinja template and attempts to perform a literal_eval on the result
    args:
        context (Jinja2 context): context information and variables to use when
            evaluating the provided template string.
        value (str): Jinja2 template string to evaluate given the provided context
        fallback_to_str (bool): If function should return string value on a failed
            attempt to literal_eval (default = True)
    returns:
        (any|None) The literal_eval'ed result, or string if fallback_to_str, or None on render failure
    raises:
        ValueError: If content is valid Python, but not a valid datatype
        SyntaxError: If content is not valid Python
    """
    context.environment.autoescape = False
    data_val = render(context, value)

    try:
        if data_val:
            data_val = literal_eval(data_val)
    except (ValueError, SyntaxError) as err:
        app.logger.debug(f"Could not literal eval {data_val}. Error: {err}")
        if not fallback_to_str:
            raise err
    context.environment.autoescape = True
    return data_val

@app.template_filter('format_date')
def format_date(value: str, default: str ="Indefinite") -> str:
    '''
    Format the provided embargo end date as a human readable string
    If there is no end date, it will show as 'Indefinite' (or the other
    default value prodived). It will only mark a valid date value as invalid
    if it is the year 9999.
    args:
        value (str): Embargo end date
    returns:
        (str): Formatted end date
    '''
    result = default

    try:
        value_date =  datetime.strptime(value, "%Y-%m-%d")
        if value_date.year != 9999:
            suf = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))
            result = value_date.strftime("%B %d %Y") # it is a valid date, so set that as the result
            day = value_date.strftime('%d')
            result = result.replace(f" {day} ", f" {suf(int(day))}, ") # Add in the suffix (st, th, rd, nd)
    except (ValueError, TypeError) as err:
        pass

    return result

@app.template_filter('sandbug')
def sandbug(value: str):
    '''
    Writes debug statements to the sandhill log
    args:
        value (str): Message to write to the log
    '''
    app.logger.debug(f"SANDBUG: {value} TYPE: {type(value)}")
    return ""


@app.template_filter('deepcopy')
def deepcopy(obj):
    """
    Returns the deepcopy of the input object
    args:
        obj (dict, list, tuple): Any value which is not a scalar type.
    """
    return copy.deepcopy(obj)

@app.template_filter('getfilterqueries')
def getfilterqueries(query: dict):
    """
    Extracts the filter queries from the solr query
    args:
        query (dict): solr query
            (ex {"q":"frogs", "fq":["dc.title:example_title1", "dc.title:example_title2", "dc.creator:example_creator1", "dc.creator:example_creator2"]})
    return:
        (dict)
        (ex. {"dc.title": ["example_title1", "example_title2"], "dc.creator": ["example_creator1", "example_creator2"]})
    """
    def parse_fq_into_dict(fq_dict, fq_str):
        fq_pair = fq_str.split(":", 1)
        if not fq_pair[0] in fq_dict:
            fq_dict[fq_pair[0]] = []
        fq_dict[fq_pair[0]].append(solr_decode(fq_pair[1]))

    fqueries = {}
    if 'fq' in query:
        if isinstance(query['fq'], list):
            for fq in query['fq']:
                parse_fq_into_dict(fqueries, fq)
        else:
            parse_fq_into_dict(fqueries, query['fq'])
    return fqueries

@app.template_filter('addfilterquery')
def addfilterquery(query: dict, field: str, value: str):
    """
    Adds the field and value to the filter query.
    Also removes the 'start' query param if it exists under the
    assumption that a user removing facets would want to return
    to the first page.
    args:
        query (dict): solr query
            (ex: {"q": "frogs", "fq": "dc.title:example_title"})
        field (str): field that needs to be checked in the fliter query
            (ex: dc.creator)
        value (str): value that needs to be checked in  the filter query
            (ex: example_creator)
    """
    if not 'fq' in query:
        query['fq'] = []

    if not isinstance(query['fq'], list):
        query['fq'] = [query['fq']]

    fquery = ':'.join([field, solr_escape(value)])
    if fquery not in query['fq']:
        query['fq'].append(fquery)

    # removing the start query param when new filters are applied
    if 'start' in query:
        del query['start']

    return query

@app.template_filter('hasfilterquery')
def hasfilterquery(query: dict, field: str, value: str):
    """
    Ensure the filter query has the field and value
    args:
        query (dict): solr query
            (ex: {"q": "frogs", "fq": "dc.title:example_title"})
        field (str): field that needs to be checked in the fliter query
            (ex: dc.title)
        value (str): value that needs to be checked in  the filter query
            (ex: example_title)
    """
    fquery = ':'.join([field, solr_escape(value)])
    found = False
    if 'fq' in query:
        if not isinstance(query['fq'], list):
            if query['fq'] == fquery:
                found = True
        else:
            if fquery in query['fq']:
                found = True
    return found

@app.template_filter('removefilterquery')
def removefilterquery(query: dict, field: str, value: str):
    """
    Removes the filter query and returns the revised query.
    Also removes the 'start' query param if it exists under the
    assumption that a user removing facets would want to return
    to the first page.
    args:
        query (dict): solr query
            (ex: {"q": "frogs", "fq": "dc.title:example_title"})
        field (str): field that needs to be removed from the fliter query
            (ex: dc.title)
        value (str): value that needs to be removed from the filter query
            (ex: example_title)
    """
    fquery = ':'.join([field, solr_escape(value)])
    if 'fq' in query:
        if not isinstance(query['fq'], list):
            if query['fq'] == fquery:
                query['fq'] = []
        else:
            if fquery in query['fq']:
                query['fq'].remove(fquery)

    # removing the start query param when new filters are applied
    if 'start' in query:
        del query['start']

    return query

@app.template_filter('maketuplelist')
def maketuplelist(input_list: list, tuple_length: int):
    """
    Convert a list into tuples of lenth tuple_length
    args:
        input_list (list): list with values that need to be converted into tuples
        tuple_length (int): length of tuples in the list
    """
    # if not evenly divisible by tuple_length excess values are discarded
    return list(zip(*[iter(input_list)]*tuple_length))

@app.template_filter('makedict')
def makedict(input_list: list):
    """
    Convert a list into a dictionary
    args:
        input_list (list): list with values that need to be converted into a dictionary
    """
    return dict(maketuplelist(input_list, 2))

