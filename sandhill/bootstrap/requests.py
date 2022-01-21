from flask import request
from sandhill import app

# Additional properties for the request object
@app.before_request
def update_request_object():
    """
    Inject values into request object
    """
    request.__dict__['query_args'] = request.args.to_dict(flat=False)

