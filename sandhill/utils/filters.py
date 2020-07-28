"""Filters for jinja templating engine"""
from .. import app

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
    #TODO fix filter name? no longer fedcom url
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
