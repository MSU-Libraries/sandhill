"""
Sandhill modifications to the Flask request object.
"""
from sandhill import app
from sandhill.utils.request import reload_request_args


# Additional properties for the request object
@app.before_request
def update_request_object():
    """
    Standard changes Sandhill makes to the default Flask `request` object.\n
    Specifically, it:\n
      - Adds `query_args`, a normal Python dictionary with args as keys. \n
    """
    reload_request_args()
