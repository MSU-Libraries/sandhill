import os
import collections
from operator import itemgetter
from flask import json, abort
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
                app.logger.warning("Missing 'value' and/or 'allowed' for 'match_condition' in: {0}".format(path))
                continue
    matched_path = max(matched_dict.items(), key=itemgetter(1))[0] if matched_dict else None

    for path, score in matched_dict.items():
        app.logger.debug("load_matched_json - score: {0}, path: {1}".format(score, path))

    # Ensure number of matches is greater than 0
    if matched_path in matched_dict and matched_dict[matched_path]:
        app.logger.info("load_matched_json - matched: {0}".format(matched_path))
        file_data = config_files[matched_path]

    return file_data
