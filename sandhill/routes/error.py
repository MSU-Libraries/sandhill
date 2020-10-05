"""
This is to override the default abort code pages and apply a
different template to them
"""
from werkzeug.exceptions import HTTPException
from flask import render_template, jsonify
from sandhill import app
from sandhill.utils.request import match_request_format

@app.errorhandler(HTTPException)
def handle_http_abort(exc):
    """Override the default template for abort codes"""

    # Check if the request accepts json format, if so prefer that for rendering
    request_format = match_request_format(None, ["application/json", "text/html"])
    if request_format == "application/json":
        exc_dict = {"code": exc.code, "name": exc.name, "description": exc.description}
        return jsonify(exc_dict), exc.code

    # Otherwise return html
    return render_template("abort.html.j2", e=exc), exc.code
