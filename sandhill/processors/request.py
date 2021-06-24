'''
Processor for requests
'''
from flask import request, jsonify, abort
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException
import requests
from sandhill import app

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
        "url_root": request.url_root,
        "query_args": request.args.to_dict(flat=False)
    }
    return url_components

def api_json(data_dict):
    '''
    Make a call to an API and return the response content as JSON
    '''
    try:
        app.logger.debug(f"Connecting to {data_dict['url']}")
        response = requests.request(method=data_dict["method"], url=data_dict["url"])

        if not response.ok:
            app.logger.warning(f"Call to {data_dict['url']} returned a non-ok status code: {response.status_code}. {response.__dict__}")
            abort(resp.status)

        response = response.json()
    except RequestException as exc:
        app.logger.warning(f"Call to {data_dict['url']} returned {response.status_code}. {response.__dict__}")
        abort(503)
    except JSONDecodeError:
        app.logger.error(f"Call returned from {data_dict['url']} that was not JSON.")
        abort(503)
    return response
