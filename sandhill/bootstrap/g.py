'''
Sandhill additions to the Flask 'g' variable.
'''
from flask import g, appcontext_pushed
from sandhill import app

def g_set(_):
    """
    Standard changes Sandhill makes to the default Flask `g` object.\n
    Specifically, it:\n
      - Adds `instance_path` available in `g` object.
    """
    g.instance_path = app.instance_path # pylint: disable=assigning-non-slot

appcontext_pushed.connect(g_set, app)
