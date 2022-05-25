"""
Modify Flask responses to set cache disabling headers.
"""
from sandhill import app

@app.after_request
def disable_browser_cache(response):
    """Adds headers to disable browser caching when app is in debug mode."""
    if app.debug:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = 0
    return response
