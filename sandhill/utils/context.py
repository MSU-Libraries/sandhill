"""Context related functionality"""
from typing import Any  # pylint: disable=unused-import
from datetime import datetime
from copy import deepcopy
from deepdiff import DeepDiff
from flask import request, has_app_context
from jinja2 import pass_context
from sandhill import app
import json

def app_context():
    """
    Create a flask app context if not already present.\n
    ```
    # Example use
    with context.app_context():
        ...
    ```
    Returns:
        A context manager class instance.
    """
    class NullContext: # pylint: disable=all
        def __enter__(self): return None
        def __exit__(self, exc_type, exc_value, traceback): return None

    return app.app_context() if not has_app_context() else NullContext()

def list_custom_context_processors():
    """
    Get the full list of the available custom context processors.
    Returns:
        (list): A list of strings of the context processor names.
    """
    custom = []
    for entries in app.template_context_processors[None]:
        ctx_procs = entries()
        for key in ctx_procs:
            if key not in ['g', 'request', 'session']:
                custom.append(key)
    return custom

@app.context_processor
def context_processors():
    """
    The list of  Sandhill context processor functions.
    Returns:
        (dict): Context processors mapped as: name => function
    """
    # TODO move function definitions to sandhill/context/ and import them for use below

    def strftime(fmt: str = None, day: str = None) -> str:
        """
        Wrapper around datetime.strftime with default yyyy-mm-dd format
        args:
            fmt (str): The format for the date to return
            day (str): A date in yyyy-mm-dd format to format, or today if not passed
        returns:
            (str): The formatted date
        """
        fmt = "%Y-%m-%d" if not fmt else fmt
        day = datetime.now() if not day else datetime.strptime(day, "%Y-%m-%d")
        return day.strftime(fmt)

    def context_sandbug(value: Any, comment: str = None):
        """
        Sandbug as a context processor, because we can. Will output the given
        value into the logs. For debugging.
        Args:
            value (Any): The value to debug.
            comment (str): Additional comment to add to log output.
        Returns:
            (None): Sandbug does not return a value.
        """
        sandbug(value, comment) # pylint: disable=undefined-variable

    def urlcomponents():
        """
        Creates a deepcopy of the url components part of the request object.
        Returns:
            (dict): The copied data.
        """
        return {
            "path": str(request.path),
            "full_path": str(request.full_path),
            "base_url": str(request.base_url),
            "url": str(request.url),
            "url_root": str(request.url_root),
            "query_args": deepcopy(request.query_args),
            "host": str(request.host)
        }

    def find_mismatches(dict1: dict, dict2: dict) -> dict:
        """
        Return detailed info about how and where the two supplied dicts don't match.
        Args:
            dict1 (dict): A dictionary to compare.
            dict2 (dict): A dictionary to compare.
        Returns:
            (dict) A dictionary highlighting what is different between the two inputs.
        """
        return dict(DeepDiff(dict1, dict2, ignore_order=True))

    @pass_context
    def get_var(context, var: str):
        """
        Returns the given variable in the current application context
        Args:
            var (str): The name of the variable to get from the context
        Returns:
            (any): The value of the provided variable in the current context
        """
        ctx = dict(context)
        return ctx[var] if var in ctx else None

    # Mapping of context function names to actual functions
    return {
        'debug': app.debug,
        'strftime': strftime,
        'sandbug': context_sandbug,
        'urlcomponents': urlcomponents,
        'find_mismatches': find_mismatches,
        'get_var': get_var
    }
