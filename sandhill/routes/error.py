"""
This is to override the default abort code pages and apply a
different template to them
"""
from werkzeug.exceptions import HTTPException
from flask import render_template
from sandhill import app

@app.errorhandler(HTTPException)
def handle_http_abort(exc):
    """Override the default template for abort codes"""
    return render_template("abort.html.j2", e=exc), exc.code
