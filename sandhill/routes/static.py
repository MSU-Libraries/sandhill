import os
from flask import send_from_directory
from sandhill import app


@app.route('/static/<path:static_file>')
def handle_static(static_file):
    # Return from instance/static/ if available
    static_path = os.path.join(app.instance_path, "static")
    # Fall back to sandhill/static/
    if not os.path.isfile(os.path.join(static_path, static_file)):
        static_path = os.path.join(app.root_path, "static")
    if not os.path.isdir(os.path.join(static_path)):
        raise RuntimeError("No static folder for this object")
    cache_timeout = app.get_send_file_max_age(static_file)
    return send_from_directory(static_path, static_file, cache_timeout=cache_timeout)
