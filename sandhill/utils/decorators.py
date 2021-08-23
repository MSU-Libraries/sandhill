'''
Flask decorator utilities
'''
from functools import wraps
from flask import json, abort
from sandhill import app
from sandhill.utils.config_loader import get_all_routes

def catch(exc_class, exc_msg, **kwargs):
    """
    Catch general exceptions and handle in a standarized manor
    args:
        exc_class(Exception): Type of exception to catch
        exc_msg(String): Message to log with the
            parameter {exc} available in the string template.
            Ex: f"Error: {exc}"
        kwargs:
            return_val(any): Value to return after the
                exception has been handled
            abort(int): Status code to abort with
    returns:
        (any): If return_val is provided in kwargs
    throws:
        (HTTPException): If no return_val is provided in kwargs
    """
    def inner(func):
        @wraps(func)
        def wrapper(*args, **func_kwargs):
            try:
                rval = func(*args, **func_kwargs)
            except exc_class as exc:
                # Re-map the function arguments to their variable name
                # for use in formatted error message string
                args_names = func.__code__.co_varnames[:func.__code__.co_argcount]
                args_dict = {**dict(zip(args_names, args)), **func_kwargs}
                args_dict['exc'] = exc

                # Handling of the exception
                app.logger.error(exc_msg.format(**args_dict))

                # Return or abort as specified
                if 'return_val' not in kwargs:
                    abort(kwargs.get('abort', 500))
                rval = kwargs.get('return_val')
            return rval
        return wrapper
    return inner

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
