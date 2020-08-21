import os
import collections
from operator import itemgetter
from flask import json, abort
from sandhill import app
from sandhill.utils.config_loader import load_json_configs
from sandhill.utils.template import render_template, evaluate_conditions


def load_json(data_dict, base_path=None):
    if not base_path:
        base_path = app.instance_path
    print(base_path)
    file_data = collections.OrderedDict()

    # loop over each provided path and stop when one is found
    if 'paths' in data_dict:
        for path in data_dict['paths']:
            full_path = os.path.join(base_path, path)
            print(full_path)
            if os.path.exists(full_path):
                file_data = json.load(open(full_path), object_pairs_hook=collections.OrderedDict)
                break

    return file_data


def load_matched_json(data_dict, base_path=None):
    """
    Loads all the config files and returns the file that has the maximum matched conditions
    """
    if not base_path:
        base_path = app.instance_path
    file_data = None
    matched_dict = {}
    config_dir_path = None
    if 'location' in data_dict:
        config_dir_path = os.path.join(base_path, data_dict['location'])
    if not os.path.exists(config_dir_path):
        app.logger.error( "Unable to load config files at path {0}.".format(config_dir_path))
        if 'on_fail' in data_dict:
            abort(data_dict['on_fail'])
    else:
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
