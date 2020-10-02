import os
import io
import collections
from operator import itemgetter
from flask import json, abort
from requests.models import Response as RequestsResponse
from sandhill import app
from sandhill.utils.config_loader import load_json_configs, load_json_config
from sandhill.utils.template import render_template, evaluate_conditions


def load_json(data_dict):
    file_data = collections.OrderedDict()
    # loop over each provided path and stop when one is found
    if 'paths' in data_dict:
        for path in data_dict['paths']:
            full_path = os.path.join(app.instance_path, path)
            if os.path.exists(full_path):
                file_data = load_json_config(full_path)
                break

    return file_data

def create_json_response(data_dict):
    '''
    Wrapper for load_json that will return a json response object.
    This can be used if you wish to stream json instead of use it's data
    for a template.
    args:
        data_dict(dict): context data as defined in the route_config that has already been loaded
    returns:
        Response: response object with the json data loaded
    '''
    resp = RequestsResponse()
    resp.status_code = 200

    content = load_json(data_dict)

    if content:
        resp.raw = io.StringIO(json.dumps(content))

    return resp

def load_matched_json(data_dict):
    """
    Loads all the config files and returns the file that has the maximum matched conditions
    """
    file_data = None
    matched_dict = {}
    config_dir_path = None
    if 'location' in data_dict:
        config_dir_path = os.path.join(app.instance_path, data_dict['location'])

    config_files = load_json_configs(config_dir_path, recurse=True)
    for path, config in config_files.items():
        if "match_conditions" in config:
            match_configs = config['match_conditions']
            try:
                matched_dict[path] = evaluate_conditions(config['match_conditions'], data_dict)
            except KeyError as exc:
                app.logger.warning("Missing 'evaluate' and/or 'match_when' for 'match_condition' in: {0}".format(path))
                continue
    matched_path = max(matched_dict.items(), key=itemgetter(1))[0] if matched_dict else None

    for path, score in matched_dict.items():
        app.logger.debug("load_matched_json - score: {0}, path: {1}".format(score, path))

    # Ensure number of matches is greater than 0
    if matched_path in matched_dict and matched_dict[matched_path]:
        app.logger.info("load_matched_json - matched: {0}".format(matched_path))
        file_data = config_files[matched_path]

    return file_data
