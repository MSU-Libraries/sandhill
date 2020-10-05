'''
Processor for requests
'''
from flask import request

def get_url_components(data_dict): # pylint: disable=unused-argument
    '''
    Get current url and return dictionary of components.
    Note: pylint disable for unused-argument is because all processors must accept this param
    args:
        data_dict(dict): (not used) the route_config data and context data
    returns:
        dict: portions of the current request
    '''
    url_components = {
        "path": request.path,
        "full_path": request.full_path,
        "base_url": request.base_url,
        "url": request.url,
        "query_args": request.args.to_dict(flat=False)
    }
    return url_components
