"""
Custom middleaware for Sandhill
"""
from sandhill import app

class SandhillMiddleware:
    """
    Middleware to cache WSGI prior to starting Flask.
    This is so we have the request available to add to logs if
    Flask throws an exception prior to initializing the request object.
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        app.environ = environ
        return self.app(environ, start_response)
app.wsgi_app = SandhillMiddleware(app.wsgi_app)
