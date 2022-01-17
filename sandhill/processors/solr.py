'''
Processor for Solr requests
'''
from urllib.parse import urlencode
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException
from flask import jsonify, abort
from sandhill.utils.api import api_get, establish_url
from sandhill import app, catch
from sandhill.utils.generic import get_descendant, ifnone, get_config
from sandhill.utils.request import match_request_format, overlay_with_query_args
from sandhill.processors.file import load_json
from sandhill.utils.error_handling import dp_abort

@catch(RequestException, "Call to Solr failed: {exc}", abort=503)
@catch(JSONDecodeError, "Call returned from Solr that was not JSON.", abort=503)
@catch(KeyError, "Missing url component: {exc}", abort=400) # Missing 'params' key
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

    # query solr with the parameters
    app.logger.debug(f"Connecting to {url}?{urlencode(data_dict['params'])}")
    response = api_get_function(url=url, params=data_dict['params'])
    response_json = None
    if not response.ok:
        app.logger.warning(f"Call to Solr returned {response.status_code}. {response}")
        try:
            if 'error' in response.json():
                app.logger.warning(
                    f"Error returned from Solr: {str(response.json()['error'])}")
        except JSONDecodeError:
            pass
        dp_abort(response.status_code)
    else:
        response_json = response.json()
        # Get the records that exist at the provided record_keys
        if 'record_keys' in data_dict and data_dict['record_keys']:
            response_json = get_descendant(response_json, data_dict['record_keys'])

    return response_json

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
    data_dict['record_keys'] = ifnone(data_dict, 'record_keys', 'response.docs')
    records = select(data_dict, url, api_get_function)

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
