"""
Wrappers for making API calls to a Solr node.
"""
from collections.abc import Sequence
from urllib.parse import urlencode
from json.decoder import JSONDecodeError
from urllib3.exceptions import HTTPError
from requests.exceptions import RequestException
from flask import jsonify, abort
from sandhill.utils.api import api_get, establish_url
from sandhill import app, catch
from sandhill.utils.generic import getdescendant, ifnone, getconfig, recursive_merge
from sandhill.utils.request import overlay_with_query_args
from sandhill.utils.response import to_response
from sandhill.processors.file import load_json
from sandhill.utils.error_handling import dp_abort

@catch((RequestException, HTTPError), "Call to Solr failed: {exc}", abort=503)
@catch(JSONDecodeError, "Call returned from Solr that was not JSON.", abort=503)
@catch(KeyError, "Missing url component: {exc}", abort=400) # Missing 'params' key
def select(data, url=None, api_get_function=api_get):
    """
    Perform a Solr select call and return the loaded JSON response. \n
    ```json
    "name": "mysearch",
    "processor": "solr.select",
    "params": { "q": "*", "rows":"20" }
    ``` \n
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `params` _dict_: Query arguments to pass to Solr.\n
            * `record_keys` _string, optional_: Return this [descendant path](#TODO) from \
              the response JSON.\n
        url (str): Overrides the default SOLR_URL normally retrieved from \
                   the [Sandhill config](#TODO) file.\n
        api_get_function (function): Function used to call Solr with. Used in unit tests.\n
    Returns:
        (dict|None): The loaded JSON data or None if nothing matched. \n
    Raises:
        wergzeug.exceptions.HTTPException: If `on_fail` is set. \n
    """

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
        if 'wt' in data['params'] and data['params']['wt'] != 'json':
            return response.text
        response_json = response.json()
        # Get the records that exist at the provided record_keys
        if 'record_keys' in data and data['record_keys']:
            response_json = getdescendant(response_json, data['record_keys'])

    return response_json


def select_record(data, url=None, api_get_function=api_get):
    """
    Perform a Solr select call and return the first result from the response. \n
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `params` _dict_: Query arguments to pass to Solr.\n
            * `record_keys` _string, optional_: Return this [descendant path](#TODO) from \
              the response JSON. Default: `response.docs`\n
        url (str): Overrides the default SOLR_URL normally retrieved from the \
                   [Sandhill config](#TODO) file.\n
        api_get_function (function): Function used to call Solr with. Used in unit tests.\n
    Returns:
        (Any): The first item matched by `record_keys` in the JSON response, otherwise None. \n
    Raises:
        wergzeug.exceptions.HTTPException: If `on_fail` is set. \n
    """
    data['record_keys'] = ifnone(data, 'record_keys', 'response.docs')
    records = select(data, url, api_get_function)

    if records and isinstance(records, Sequence):
        return records[0]
    return None


def search(data, url=None, api_get_function=api_get):
    """
    Perform a [configured Solr search](#TODO) and return the result. \n
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
        (dict|flask.Response): A dict of the loaded JSON response, or a `flask.Response` instance \
                               if `view_args.format` is `text/json`. \n
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
    if 'config_ext' in data and 'solr_params' in data['config_ext']:
        solr_config = recursive_merge(
            search_config['solr_params'],
            data['config_ext']['solr_params']
        )
    else:
        solr_config = search_config['solr_params']

    # override default parameters with request query parameters
    data['params'] = overlay_with_query_args(solr_config,
            request_args=data.get('params', None),
            allow_undefined=True)

    extension = get_requested_extension(data)
    if not is_valid_extension(extension):
        abort(501)
    writer = get_writer_from_extension(extension)
    data['params']['wt'] = writer
    solr_results = select(data, url, api_get_function)

    return get_extension_callback(extension)(solr_results)


def get_requested_extension(data) -> str:
    """
    Extract the extension requested from the request (or modified by another processor).
    Args:
        data (list): Processor arguments and all other data loaded from previous data processors.\n
    Returns:
        (str): The requested extension.\n
    """
    view_args = data.get('view_args')
    return view_args.get('format') if view_args else None


def is_valid_extension(ext: str) -> bool:
    """
    Return if the given extension has corresponding mapping.
    Args:
        ext (str): The extension.\n
    Returns:
        (str): True if the extension has corresponding mappings, False otherwise.\n
    """
    return ext in extension_writer_mapping() and ext in extension_callback_mapping()


def extension_writer_mapping() -> dict:
    """
    Return the mapping with the form {extension: solr_writer}.
    Args:
    Returns:
        (dict): The dict containing the mapping in between extension and writer.\n
    """
    # extension: solr_writer
    return {
        None: 'json',
        'html': 'json',
        'json': 'json',
        'csv': 'csv',
        'py': 'python',
        'rb': 'ruby',
        # 'xlsx': 'xlsx', # needs additional solr config
        'xml': 'xml',
        # 'xslt': 'xslt', # seems to need additional solr config
    }


def get_writer_from_extension(ext: str|None) -> str:
    """
    Get the corresponding writer for the given extension.
    Args:
        ext (str|any): The extension.\n
    Returns:
        (str): The solr writer. \n
    """
    return extension_writer_mapping()[ext]


def get_extension_callback(ext: str):
    """
    Get the corresponding callback for the given extension.
    Args:
        ext (str): The extension.\n
    Returns:
        (str): The corresponding callback to execute for this extension.\n
    """
    # We already tested if it exists with is_valid_extension
    return extension_callback_mapping()[ext]


def raw_parameter(param: any) -> any:
    """
    Return the given parameter as passed.
    Args:
        param (any): The parameter to get back.\n
    Returns:
        (any): The given parameter. \n
    """
    return param


def extension_callback_mapping() -> dict:
    """
    Return the mapping with the form {extension: callback}.
    Args:
    Returns:
        (dict): The dict containing the mapping in between extension and callback.\n
    """
    return {
        # extension: callback
        None: raw_parameter, # do nothing
        'html': raw_parameter, # do nothing
        'json': jsonify,
        'csv': to_response,
        'py': to_response,
        'rb': to_response,
        'xml': to_response,
    }
