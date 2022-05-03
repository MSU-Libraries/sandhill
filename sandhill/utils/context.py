"""Context related functionality"""
from datetime import datetime
from copy import deepcopy
from deepdiff import DeepDiff
from flask import request, has_app_context
from sandhill import app
import json

def app_context():
    """
    Create a flask app context if not already present.
    Use example:
        with context.app_context():
            ...
    """
    class NullContext: # pylint: disable=all
        def __enter__(self): return None
        def __exit__(self, exc_type, exc_value, traceback): return None

    return app.app_context() if not has_app_context() else NullContext()

def list_custom_context_processors():
    """
    Get a list of the current custom context processors
    returns:
        (list): A list of strings of the names
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
    Added context processor functions
    """
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

    def context_sandbug(value: str, comment: str = None):
        """
        Sandbug as a context processor, because we can.
        """
        sandbug(value, comment) # pylint: disable=undefined-variable

    def urlcomponents():
        """
        Create a copy of the url components part of the request object
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
    def find_mismatches(dict1: dict, dict2: dict):
        """
        Return detailed info about how and where the two supplied dicts don't match.
        """
        return dict(DeepDiff(dict1, dict2, ignore_order=True))

    return {
        'debug': app.debug,
        'strftime': strftime,
        'sandbug': context_sandbug,
        'urlcomponents': urlcomponents,
        'find_mismatches': find_mismatches
    }
