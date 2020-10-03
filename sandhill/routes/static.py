'''
Handle static files being served
'''

import os
from flask import send_from_directory
from sandhill import app


@app.route('/static/<path:static_file>')
def handle_static(static_file):
    '''
    Retrieve the requested static file first looking for /static in the instance
    directory and falling back to the sandhill/static directory if /static not found
    within the instance.

    args:
        static_file (str): requested file within /static
    returns:
        file stream of the object
    '''
    # Return from instance/static/ if available
    static_path = os.path.join(app.instance_path, "static")

    # Fall back to sandhill/static/
    if not os.path.isfile(os.path.join(static_path, static_file)):
        static_path = os.path.join(app.root_path, "static")

    cache_timeout = app.get_send_file_max_age(static_file)
    return send_from_directory(static_path, static_file, cache_timeout=cache_timeout)

@app.route('/favicon.ico')
def favicon():
    '''
    Wrapper for calling handle_static for specifically the favicon file
    returns:
        file stream of the favicon.ico file
    '''
    return handle_static('favicon.ico')
