'''
Processor for Solr requests
'''
import os
from urllib.parse import urlencode
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException
from flask import jsonify, abort
from sandhill.utils.api import api_get, establish_url
from sandhill import app
from sandhill.utils.generic import get_descendant_from_dict, ifnone, get_config
from sandhill.utils.request import match_request_format, overlay_with_query_args
from sandhill.processors.file import load_json

def select(data_dict, url=None, api_get_function=api_get):
    '''
    Performs a Solr select call
    args:
        data_dict(dict): route_config data and other data loaded in context
        url(str): Override the default solr URL stored in SOLR_URL of the app config
        api_get_function(function): function to use to call Solr with
    returns:
        json: response from solr
    '''

    response = None
    url = establish_url(url, get_config('SOLR_URL', None))
    url = url + "/select"

    try:
        # query solr with the parameters
        app.logger.debug("Connecting to {0}?{1}".format(url, urlencode(data_dict['params'])))
        response = api_get_function(url=url, params=data_dict['params'])

        if not response.ok:
            app.logger.warning(f"Call to Solr returned {response.status_code}. {response}")
            try:
                if 'error' in response.json():
                    app.logger.warning(
                        "Error returned from Solr: {0}".format(str(response.json()['error'])))
            except JSONDecodeError:
                pass
            abort(response.status_code)

        response = response.json()
    except RequestException as exc:
        app.logger.warning("Call to Solr failed: {0}".format(exc))
        abort(503)
    except JSONDecodeError:
        app.logger.error("Call returned from Solr that was not JSON.")
        abort(503)
    # Catch for missing 'params' key
    except KeyError as exc:
        app.logger.error("Missing url component: {0}".format(exc))
        abort(400)

    return response

def select_record(data_dict, url=None, api_get_function=api_get):
    '''
    Select a single record from solr, specifically the first one
    args:
        data_dict(dict): route_config data and other data loaded in context
        url(str): Override the default solr URL stored in SOLR_URL of the app config
        api_get_function(function): function to use to call Solr with
    returns:
        json: response from solr giving the first record in the response
    '''
    json_data = select(data_dict, url, api_get_function)

    # Get the records that exist at the provided record_keys
    record_keys = ifnone(data_dict, 'record_keys', 'response.docs')
    records = get_descendant_from_dict(json_data, record_keys.split('.') if record_keys else [])

    if records:
        return records[0]
    return None

def search(data_dict, url=None, api_get_function=api_get):
    """
    Searches solr and gets the results
    args:
        data_dict (dict) :  route config settings for searching
    returns:
        Response (from flask): If result_format is 'test/json'
        dict: All other cases
    """
    if 'paths' not in data_dict or not data_dict['paths']:
        app.logger.error(
            f"Missing 'config' setting for processor "
            f"'{data_dict['processor']}' with name '{data_dict['name']}'")
        abort(500)

    # Load the search settings
    search_config = load_json(data_dict)
    if 'solr_params' not in search_config:
        app.logger.error(
            f"Missing 'solr_params' inside search config file(s) '{ str(data_dict['paths']) }'")
        abort(500)
    solr_config = search_config['solr_params']

    # override default parameters with request query parameters (if allowed by config)
    data_dict['params'] = overlay_with_query_args(solr_config, \
            request_args=data_dict.get('params', None))

    solr_results = select(data_dict, url, api_get_function)

    # check if the json results were requested
    result_format = match_request_format('format', ['text/html', 'application/json'])
    if result_format == 'application/json':
        solr_results = jsonify(solr_results)

    return solr_results
