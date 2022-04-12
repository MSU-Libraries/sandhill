"""
Requests related functions
"""
import mimetypes
from copy import deepcopy
from flask import request, abort
from sandhill.utils.generic import touniquelist

def match_request_format(view_args_key, allowed_formats, default_format='text/html'):
    """
    Match a request mimetype to the given view_args_key or the allowed mimetypes provided by client.

    args:
        view_args_key (str|None): the key in the url request to check within for matching format.
        allowed_formats (list): list of acceptable mimetypes.
    kwargs:
        default_format (str): the mimetype to use by default if view_args_key value is not allowed.
    returns:
        result_format (str): the mimetype for the format to return.
    """
    result_format = default_format
    # check for accept header
    for mtype, _ in list(request.accept_mimetypes):
        if mtype in allowed_formats:
            result_format = mtype
            break

    # check for ext; e.g. search.json
    if request.view_args and view_args_key in request.view_args:
        mimetypes.init()
        extension = "." + request.view_args[view_args_key]
        if extension in mimetypes.types_map:
            result_format = mimetypes.types_map[extension]

    if result_format not in allowed_formats:
        abort(501)

    return result_format


def overlay_with_query_args(query_config, request_args=None, *, allow_undefined=False):
    """Given a query config, overlay request.args on the defaults to generate a combined
    list of query arguments
    args:
        query_config(dict): A dictionary containing rules for query args to parse, each key being a
                            query arg name (e.g. "arg_name").
            Format for each key as below:
                "arg_name": {
                    "base": ["value"]
                      -- Optional (str | list): value that cannot be changed by request.args; will
                         always be returned
                    "default": ["overridable"]
                      -- Optional (str | list): value which will be replaced by matching
                         requst.args, if passed
                }
            Either "base" or "default" is required. If appropriate "arg_name" is not passed,
            that "arg_name" will be filtered out. If "default" is not set, the request,arg
            matching "arg_name" will be filtered out. Both "base" and "default" may be set at
            the same time. In this case, only the "default" value will be able to be
            overridded by requests.args; the "base" will remain unchanged.
        request_args (dict):
        allow_undefined (bool): If True, fields not defined in the query_config will be permitted
    return: A dict of the combined query arguments
    """
    # grab the query string params and convert to a flat dict if request args not passed in
    # i.e. duplicative keys will be converted to a list of strings
    if request_args is None:
        request_args = request.args.to_dict(flat=False)
    else:
        # avoid modifying incoming args dict
        request_args = deepcopy(request_args)

    query_params = {}
    for field_name, field_conf in query_config.items():
        query_params[field_name] = []
        # Load base from config
        if 'base' in field_conf:
            query_params[field_name] = field_conf['base']
        # Load from request_args
        if field_name in request_args:
            # Allow override if field defined with a default
            if 'default' in field_conf:
                query_params[field_name] = touniquelist(
                    query_params[field_name],
                    request_args[field_name]
                )
            # Remove field from request_args having already processed it
            del request_args[field_name]
        # Load default from config if solr_param field not defined
        elif 'default' in field_conf:
            query_params[field_name] = touniquelist(
                query_params[field_name],
                field_conf['default']
            )
        # Remove field from solr query if empty
        if not any(query_params[field_name]):
            del query_params[field_name]

        # restrictions
        #TODO something like: query_params[field_name] = apply_restrictions(
        #    query_params[field_name], field_conf['restrictions'])
        # Anyone who puts a negative number in rows or (any other non integer) will
        # get what they deserve. "-1" for instance will return the max
        # number of search results.
        if 'max' in field_conf:
            query_params[field_name] = [
                val if str(val).isdigit() and int(val) < int(field_conf['max'])
                else str(field_conf['max']) for val in query_params[field_name]
            ]
        if 'min' in field_conf:
            query_params[field_name] = [
                val if str(val).isdigit() and int(val) > int(field_conf['min'])
                else str(field_conf['min']) for val in query_params[field_name]
            ]

    if allow_undefined:
        query_params.update(request_args)

    return query_params
