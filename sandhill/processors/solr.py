"""
Wrappers for making API calls to a Solr node.
"""
from collections.abc import Sequence
from urllib.parse import urlencode
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException
from flask import jsonify, abort
from sandhill.utils.api import api_get, establish_url
from sandhill import app, catch
from sandhill.utils.generic import getdescendant, ifnone, getconfig
from sandhill.utils.request import match_request_format, overlay_with_query_args
from sandhill.processors.file import load_json
from sandhill.utils.error_handling import dp_abort

@catch(RequestException, "Call to Solr failed: {exc}", abort=503)
@catch(JSONDecodeError, "Call returned from Solr that was not JSON.", abort=503)
@catch(KeyError, "Missing url component: {exc}", abort=400) # Missing 'params' key
def select(data, url=None, api_get_function=api_get):
    """
    Perform a Solr select call and return the loaded JSON response.
    ```json
    "name": "mysearch",
    "processor": "solr.search",
    "params": { "q": "*", "rows":"20" }
    ```
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
          * `params` _dict_: Query arguments to pass to Solr.\n
          * `record_keys` _string, optional_: Return this [descendant path](#TODO) from \
            the response JSON.\n
        url (str): Overrides the default SOLR_URL normally retrieved from \
          the [Sandhill config](#TODO) file.\n
        api_get_function (function): Function used to call Solr with. Used in unit tests.\n
    Returns:
        The loaded JSON data or None if nothing matched.
    Raises:
        wergzeug.exceptions.HTTPException: If `on_fail` is set.
    """

    response = None
    url = establish_url(url, getconfig('SOLR_URL', None))
    url = url + "/select"

    # query solr with the parameters
    app.logger.debug(f"Connecting to {url}?{urlencode(data['params'])}")
    response = api_get_function(url=url, params=data['params'])
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
        if 'record_keys' in data and data['record_keys']:
            response_json = getdescendant(response_json, data['record_keys'])

    return response_json


def select_record(data, url=None, api_get_function=api_get):
    """
    Perform a Solr select call and return the first result from the response.
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
          * `params` _dict_: Query arguments to pass to Solr.\n
          * `record_keys` _string, optional_: Return this [descendant path](#TODO) from \
            the response JSON. Default: `response.docs`\n
        url (str): Overrides the default SOLR_URL normally retrieved from the \
          [Sandhill config](#TODO) file.\n
        api_get_function (function): Function used to call Solr with. Used in unit tests.\n
    Returns:
        The first item matched by `record_keys` in the JSON response, otherwise None.
    Raises:
        wergzeug.exceptions.HTTPException: If `on_fail` is set.
    """
    data['record_keys'] = ifnone(data, 'record_keys', 'response.docs')
    records = select(data, url, api_get_function)

    if records and isinstance(records, Sequence):
        return records[0]
    return None


def search(data, url=None, api_get_function=api_get):
    """
    Perform a [configured Solr search](#TODO) and return the result.
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
          * `path` _string_, `paths` _list_: The path to a search config file. Loaded \
            per [file.load_json](#TODO).\n
          * `params` _dict_: Query arguments to pass to Solr.\n
          * `record_keys` _string, optional_: Return this [descendant path](#TODO) from \
            the response JSON. Default: `response.docs`\n
        url (str): Overrides the default SOLR_URL normally retrieved from \
          the [Sandhill config](#TODO) file.\n
        api_get_function (function): Function used to call Solr with. Used in unit tests.\n
    Returns:
        A dict of the loaded JSON response, or a `flask.Response` instance \
        if `view_args.format` is `text/json`.
    """
    # TODO module should return None and call dp_abort instead of abort
    # TODO allow "path"
    if 'paths' not in data or not data['paths']:
        app.logger.error(
            f"Missing 'config' setting for processor "
            f"'{data['processor']}' with name '{data['name']}'")
        abort(500)

    # Load the search settings
    search_config = load_json(data)
    if 'solr_params' not in search_config:
        app.logger.error(
            f"Missing 'solr_params' inside search config file(s) '{ str(data['paths']) }'")
        abort(500)
    solr_config = search_config['solr_params']

    # override default parameters with request query parameters
    data['params'] = overlay_with_query_args(solr_config, \
            request_args=data.get('params', None),
            allow_undefined=True)

    solr_results = select(data, url, api_get_function)

    # check if the json results were requested
    result_format = match_request_format('format', ['text/html', 'application/json'])
    if result_format == 'application/json':
        solr_results = jsonify(solr_results)

    return solr_results
