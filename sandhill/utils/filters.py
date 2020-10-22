"""Filters for jinja templating engine"""
import urllib
from ast import literal_eval
from sandhill import app
from sandhill.utils.generic import ifnone
from datetime import datetime
from jinja2 import contextfilter, TemplateError
from collections.abc import Hashable


@app.template_filter()
def size_format(value):
    """ Jinja filter to format the size """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    nbytes = int(value) if f"{value}".isdigit() else 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

@app.template_filter()
def is_list(value):
    """ Check if a value is a list """
    return isinstance(value, list)

@app.template_filter()
def generate_datastream_url(value, obj_type='OBJ', action="view"):
    """ Generates view and download url's
        args:
            value (str): pid of the object
            obj_type (str): type of datastream object
            action (str): view or download the datastream
    """
    pid = value.replace(":","/")

    return '/{0}/{1}/{2}'.format(pid, obj_type, action)

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
    """Take url_components (derived from Flask Request object) and return url.
    args:
        url_components (dict): compoents of the URL to build
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

@app.template_filter('format_embargo_end_date')
def format_embargo_end_date(value: str, default: str ="Indefinite") -> str:
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
            result = value # it is a valid date, so set that as the result
    except (ValueError, TypeError) as err:
        pass

    return result
