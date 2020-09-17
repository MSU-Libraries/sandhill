import os
import re
import collections
import json
from collections import OrderedDict
from sandhill import app

def load_json_config(file_path):
    """Load a json config file
    args:
        file_path (str): the full path to the json file to load
    returns:
        (dict): the contents of the loaded json file
    """
    loaded_config = collections.OrderedDict()
    try:
        app.logger.info("Loading json file at {0}".format(file_path))
        with open(file_path) as json_config_file:
            loaded_config = json.load(json_config_file, object_pairs_hook=collections.OrderedDict)
    except IOError as io_exe:
        app.logger.error("IOError loading file occured: {0}".format(io_exe))
    return loaded_config

def get_all_routes(routes_dir="route_configs"):
    '''
    Finds all the json files with within /instance/route_configs
    that contain a "route" key
    args:
        (str): the directory to look for route configs. Default = route_configs
    returns:
        (list of str): all of the route rules found
    raises:
        FileNotFoundError: when the provided directory does not exist
    '''
    route_path = os.path.join(app.instance_path, routes_dir)
    routes = []
    var_counts = {}

    for conf_file in [os.path.join(route_path, j) for j in os.listdir(route_path) if j.endswith(".json")]:
        data = load_json_config(conf_file)
        if "route" in data:
            if isinstance(data["route"],list):
                for r in data["route"]:
                    routes.append(r)
            else:
                routes.append(data["route"])

    # determine the number of variables in each route and add to dictionary
    for rule in routes:
        # re match to determine # of vars
        matches = re.findall(r'<\w+:\w+>', rule)
        var_counts[rule] = len(matches)

    # order the dictionary by lowest number of variables to greatest
    var_counts = sorted(var_counts.items(), key=lambda x: x[1])

    # return the list of the sorted routes
    return [r[0] for r in var_counts]

def load_route_config(route_rule, routes_dir="route_configs"):
    '''
    Return the json data for the provided route_config
    args:
        route_rule (str): the route rule to match to in the json configs (the `route` key)
        routes_dir (str): the path to look for route configs. Default = route_configs
    returns:
        (dict): The loaded json of the matched route config
    '''
    route_path = os.path.join(app.instance_path, routes_dir)
    for conf_file in [os.path.join(route_path, j) for j in os.listdir(route_path) if j.endswith(".json")]:
        data = load_json_config(conf_file)
        if "route" in data:
            if isinstance(data["route"],list):
                if route_rule in data["route"]:
                    break
            else:
                if data["route"] == route_rule:
                    break
    return data

def load_json_configs(path, recurse=False):
    """
    Loads all the config files in the path
    args:
        path (string): path to the dir for the configs
        recurse (bool): if set does the recursive walk into the dir
    returns:
        (dict): dictionary with a key of the file path and a value of the loaded json
    """
    config_files = {}
    for root, dirs, files in  os.walk(path):
        for config_file in files:
            if config_file.endswith('.json'):
                config_file_path = os.path.join(root, config_file)
                config_files[config_file_path] = load_json_config(config_file_path)
        if not recurse:
            break
    return config_files
