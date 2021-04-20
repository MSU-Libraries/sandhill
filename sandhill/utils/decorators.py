'''
Flask decorator utilities
'''
from flask import json
from sandhill import app
from sandhill.utils.config_loader import get_all_routes

def add_routes():
    """
    Decorator function for adding routes based on all
    json route configs in instance folder
    """
    app.logger.info("Running add_routes")
    def decorator(func, **options):
        all_routes = get_all_routes()
        app.logger.info("Loading routes: {0}".format(', '.join(all_routes)))
        for rule in all_routes:
            endpoint = options.pop('endpoint', None)
            app.logger.info(
                f"Adding URL rule: {rule}, {endpoint}, {func} {json.dumps(options)}"
            )
            app.add_url_rule(rule, endpoint, func, **options)
        return func
    return decorator
