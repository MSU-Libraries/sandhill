import os
import logging
from flask import g, abort, json
from functools import wraps
from sandhill import app
from sandhill.utils.config_loader import get_all_routes

def add_routes():
    """
    Decorator function for adding routes based on all 
    json route configs in instance folder
    """
    app.logger.info("Running add_routes")
    def decorator(f, **options):
        all_routes = get_all_routes()
        app.logger.info("Loading routes: {0}".format(', '.join(all_routes)))
        for rule in all_routes:
            endpoint = options.pop('endpoint', None)
            app.logger.info("Adding URL rule: {0}, {1}, {2} {3}".format(rule, endpoint, f, json.dumps(options)))
            app.add_url_rule(rule, endpoint, f, **options)
        return f
    return decorator
