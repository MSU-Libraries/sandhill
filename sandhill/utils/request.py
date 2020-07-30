from flask import request, abort

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
