"""Filters for jinja templating engine"""
from .. import app

@app.template_filter()
def numberFormat(value):
    """ Jinja filter to format the number """
    return format(int(value), ',d')

@app.template_filter()
def sizeFormat(value):
    """ Jinja filter to format the size """
    size =  int(value)

    kb = 1024
    mb = kb * 1024
    gb = mb * 1024
    tb = gb * 1024
    formatted_size  = str(size) + 'B'
    if size >= tb:
        formatted_size = str(round((size/tb) ,2)) + ' TB' 
    elif size >= gb:
        formatted_size = str(round((size/gb) ,2)) + ' GB'
    elif size >= mb:
        formatted_size = str(round((size/mb) ,2)) + ' MB'
    elif size >= kb:
        formatted_size = str(round((size/kb) ,2)) + ' KB'
    return formatted_size

@app.template_filter()
def is_list(value):
    """ Check if a value is a list """ 
    return isinstance(value, list)

