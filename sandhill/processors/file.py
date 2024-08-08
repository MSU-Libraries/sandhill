'''
Processing functions for files
'''
import os
import io
from operator import itemgetter
from flask import json
from requests.models import Response as RequestsResponse
from sandhill import app
from sandhill.utils.config_loader import load_json_configs, load_json_config
from sandhill.utils.template import evaluate_conditions


def load_json(data):
    '''
    Search for files at the paths within 'path' and 'paths' keys of `data`. \
    Will load JSON from the first file it finds and then return the result. \n
    If both 'path' and 'paths' are set, paths from both will be searched \
    starting with 'path' first.\n
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `path` _string_: A single file path to search for.\n
            * `paths` _list_: A list of file paths to search for.\n
    Returns:
        (dict|None): The loaded JSON data or None if no file was found.
    Note:
        Paths must be relative to the `instance/` directory.
    '''
    file_data = None
    # loop over each provided path and stop when one is found
    if "path" in data:
        data.setdefault("paths", []).insert(0, data["path"])
    if "paths" in data:
        for path in data["paths"]:
            full_path = os.path.join(app.instance_path, path.lstrip("/"))
            if os.path.exists(full_path):
                file_data = load_json_config(full_path)
                break
    return file_data

def create_json_response(data):
    '''
    Wrapper for `load_json` that will return a JSON response object. \n
    This can be used to stream JSON instead of loading it to use it as data. \n
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `path` _string_: A single file path to search for.\n
            * `paths` _list_: A list of file paths to search for.\n
    Returns:
        (requests.Response): The response object with the JSON data loaded into it.
    '''
    resp = RequestsResponse()
    resp.status_code = 200

    content = load_json(data)
    if content:
        resp.raw = io.StringIO(json.dumps(content))
    return resp

def load_matched_json(data):
    """
    Loads all the config files and returns the file that has the most [matched conditions](#TODO). \n
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `location` _string_: A directory path within the instance \
               with JSON files containing `match_conditions` keys.\n
    Returns:
        (dict|None): The loaded JSON data from the file that most matched its conditions, \
            or None if no files matched.
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
        app.logger.debug(f"load_matched_json(score={score}, path={path})")

    # Ensure number of matches is greater than 0
    if matched_path in matched_dict and matched_dict[matched_path]:
        app.logger.debug(f"load_matched_json(matched={matched_path})")
        file_data = config_files[matched_path]

    return file_data
