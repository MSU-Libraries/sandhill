'''
Sandhill overrides/additions to the  default Flask `/static` route.
'''
import os
from flask import send_from_directory
from sandhill import app

@app.route('/static/<path:filename>', endpoint='static')
def handle_static(filename):
    '''
    Replacement for the default Flask `/static` path handler.
    Retrieves the requested static file by first looking for it inside
    the `instance/static/` directory. If the file is not found, this
    method will then look for the file in the core `sandhill/templates/`
    directory.
    Args:
        filename (str): The requested file path within `/static`
    Returns:
        (file stream): File stream of the file object
    Raises:
        HTTPException: On HTTP error
    '''
    # Return from instance/static/ if available
    static_path = os.path.join(app.instance_path, "static")

    # Fall back to sandhill/static/
    if not os.path.isfile(os.path.join(static_path, filename)):
        static_path = os.path.join(app.root_path, "static")

    cache_timeout = app.get_send_file_max_age(filename)
    return send_from_directory(static_path, filename, max_age=cache_timeout)

@app.route('/favicon.ico')
def favicon():
    '''
    Wrapper to calling handle_static for the ever popular favicon file.
    Returns:
        (file stream): The favicon.ico file stream from inside `/static`
    Raises:
        HTTPException: On HTTP error
    '''
    return handle_static('favicon.ico')
