"""
Sandhill modifications to the Flask request object.
"""
from flask import request
from sandhill import app

# Additional properties for the request object
@app.before_request
def update_request_object():
    """
    Standard changes Sandhill makes to the default Flask `request` object.\n
    Specifically, it:\n
      - Adds `query_args`, a normal Python dictionary with args as keys.
    """
    request.__dict__['query_args'] = request.args.to_dict(flat=False)
