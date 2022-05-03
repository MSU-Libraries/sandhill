'''
Initialize additions to the flask 'g' variable.
'''
from flask import g, appcontext_pushed
from sandhill import app

def g_set(_):
    """
    Make instance_path available for global use.
    """
    g.instance_path = app.instance_path # pylint: disable=assigning-non-slot

appcontext_pushed.connect(g_set, app)
