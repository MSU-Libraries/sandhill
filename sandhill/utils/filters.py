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
def generate_fedcom_url(value, obj_type='OBJ', action="VIEW"):
    """ Generates view and download url's
        args:
            pid (str): pid of the object
            obj_type (str): type of datastream object
            action (str): view or download the datastream
    """
    base_url = "https://d.lib.msu.edu"
    pid = value.replace(":","/")
    obj_url = base_url

    return '{0}/{1}/datastream/{2}/{3}'.format(base_url, pid, obj_type, action)

@app.template_filter()
def solr_first_item(value):
    """ Check if a value is a list and returns the first item"""
    if isinstance(value, list):
        value = value[0]
    return value

