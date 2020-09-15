"""Filters for jinja templating engine"""
import urllib
from ast import literal_eval
from sandhill import app
from sandhill.utils.generic import ifnone
from datetime import datetime
from jinja2 import contextfilter, TemplateError


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
    """Filter to escape a value being passed to Solr"""
    escapes = { ' ': r'\ ', '+': r'\+', '-': r'\-', '&': r'\&', '|': r'\|', '!': r'\!',
                '(': r'\(', ')': r'\)', '{': r'\{', '}': r'\}', '[': r'\[', ']': r'\]',
                '^': r'\^', '~': r'\~', '*': r'\*', '?': r'\?', ':': r'\:', '"': r'\"',
                ';': r'\;' }
    value = value.replace('\\', r'\\')  # must be first replacement
    for k,v in escapes.items():
        value = value.replace(k,v)
    return value

@app.template_filter('set_query_arg')
def set_query_arg(url_components, key, value):
    """Take dictionary of url components, and update 'key' with 'value'."""
    url_components['query_args'][key] = value

    return url_components

@app.template_filter('assemble_url')
def assemble_url(url_components):
    """Take url_components (derived from Flask Request object) and return url."""
    return url_components["path"] + "?" + urllib.parse.urlencode(url_components["query_args"], doseq=True)

@app.template_filter('date_passed')
def date_passed(value):
    """ Checks if the embargoded date is greater than the current date"""
    value_date =  datetime.strptime(value, "%Y-%m-%d")
    current_date  = datetime.now()
    if value_date.date() < current_date.date():
        return True
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
