"""
Modify responses to disable caching
"""
from sandhill import app

@app.after_request
def disable_browser_cache(response):
    """
    When app is in debug mode, add headers to disable browser caching
    Args:
        response (flask.Response): The completed response before sending to the client
    Returns:
        response (flask.Response): The final response, potentially modified
    """
    if app.debug:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = 0
    return response
