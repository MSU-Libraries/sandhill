'''
Processing functions for files
'''
import os
import io
import collections
from operator import itemgetter
from flask import json
from requests.models import Response as RequestsResponse
from sandhill import app
from sandhill.utils.config_loader import load_json_configs, load_json_config
from sandhill.utils.template import evaluate_conditions


def load_json(data):
    '''
    Looks for paths within the 'paths' key of the data and will
    search for those files within the instance directory. It will stop
    when it finds a file and will return the contents as json.
    args:
        data(dict): all of the previously loaded data, typically from a route
    returns:
        json: The first file found in the instance_path with the given path
    '''
    file_data = collections.OrderedDict()
    # loop over each provided path and stop when one is found
    if 'paths' in data:
        for path in data['paths']:
            full_path = os.path.join(app.instance_path, path)
            if os.path.exists(full_path):
                file_data = load_json_config(full_path)
                break

    return file_data

def create_json_response(data):
    '''
    Wrapper for load_json that will return a json response object.
    This can be used if you wish to stream json instead of use it's data
    for a template.
    args:
        data(dict): all of the previously loaded data, typically from a route
    returns:
        Response: response object with the json data loaded
    '''
    resp = RequestsResponse()
    resp.status_code = 200

    content = load_json(data)

    if content:
        resp.raw = io.StringIO(json.dumps(content))

    return resp

def load_matched_json(data):
    """
    Loads all the config files and returns the file that has the maximum matched conditions
    args:
        data(dict): context data as previously loaded, typically from a route
    returns:
        json: data from the matched route config based on the most match_conditions
    """
    file_data = None
    matched_dict = {}
    config_dir_path = None
    if 'location' in data:
        config_dir_path = os.path.join(app.instance_path, data['location'])

    config_files = load_json_configs(config_dir_path, recurse=True)
    for path, config in config_files.items():
        if "match_conditions" in config:
            try:
                matched_dict[path] = evaluate_conditions(config['match_conditions'], data)
            except KeyError:
                app.logger.warning(
                    f"Missing 'evaluate' and/or 'match_when' for 'match_condition' in: {path}")
                continue
    matched_path = max(matched_dict.items(), key=itemgetter(1))[0] if matched_dict else None

    for path, score in matched_dict.items():
        app.logger.debug(f"load_matched_json - score: {score}, path: {path}")

    # Ensure number of matches is greater than 0
    if matched_path in matched_dict and matched_dict[matched_path]:
        app.logger.info(f"load_matched_json - matched: {matched_path}")
        file_data = config_files[matched_path]

    return file_data
