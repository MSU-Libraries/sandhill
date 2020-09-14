"""Filters for jinja templating engine"""
import urllib
from ast import literal_eval
from sandhill import app
from sandhill.utils.generic import ifnone
from datetime import datetime
from jinja2 import contextfilter, TemplateError


@app.template_filter()
def number_format(value):
    """ Jinja filter to format the number """
    return format(int(value), ',d')

@app.template_filter()
def size_format(value):
    """ Jinja filter to format the size """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    nbytes =  int(value) if value else 0
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
    """If value is a list, returns the head of the list, otherwise return the value as is"""
    if isinstance(value, list):
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
def render(context, value, to_str=True):
    """Renders a given string or literal
    args:
        context (Jinja2 context): context information and variables to use when 
            evaluating the provided template string.
        value (str): Jinja2 template string to evaluate given the provided context
        to_str (bool): If it should return a string of the rendered template to it
            or attempt a literal_eval to convert it to it's datatype (default = True)
    returns:
        (str|any): the rendered value or string
    """
    data_val = ''
    context.environment.autoescape = to_str if isinstance(to_str, bool) else False

    try:
        data_template = context.environment.from_string(value)
        data_val = data_template.render(**context)

        if not to_str:
            data_val = literal_eval(data_val) # TODO -- this throws an exception for metadata fields not in solr record
    except (ValueError,SyntaxError) as err:
        app.logger.warning(f"Could not literal eval {data_val}. Error: {err}")
    except TemplateError as terr:
        app.logger.warning(f"Invalid template provided: {value}. Error: {terr}")

    context.environment.autoescape = True
    return ifnone(data_val,'')

