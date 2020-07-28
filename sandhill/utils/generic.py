"""
Generic function that can be used in any context
"""
from flask import request, abort

def ifnone(var, default_val):
    '''
    Returns var if it is not None else the default_val
    '''
    return var if var else default_val

def ifnone(var, key, default_val):
    '''
    Returns var[key] if key in var else the default_val
    '''
    return var[key] if key in var else default_val

def combine_to_list(*args):
    """
    Combine a and b, which may be a scalar variable or list, and returns them as a list
    """
    combined = []
    for x in args:
        if isinstance(x, list):
            combined += x
        else:
            combined.append(x)
    return combined


def match_request_format(view_args_key, allowed_formats, default_format='text/html'):
    """
    Match a request mimetype to the given view_args_key or the allowed mimetypes provided by client.
    """
    result_format = default_format
    # check for accept header
    for mtype in list(request.accept_mimetypes):
        if mtype in allowed_formats:
           result_format = mtype
           break

    # check for ext; e.g. search.json
    if view_args_key in request.view_args:
        result_format = "text/" + request.view_args[view_args_key]  # TODO refactor into mimetype function

    if result_format not in allowed_formats:
        abort(501)

    return result_format
