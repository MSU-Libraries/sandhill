'''
Jinja bootstrap
'''
from sandhill import app

def configure_jinja():
    '''
    Perform any configuration of the Jinja
    environment
    '''
    # Remove exta whitespace from page templates
    # to reduce page size
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
