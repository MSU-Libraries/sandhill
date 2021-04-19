import os
import re
import collections
import operator
import json
from json.decoder import JSONDecodeError
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
    except OSError as o_err:
        app.logger.error(f"Unable to read json file at path: {file_path} Error: {o_err}")
    except JSONDecodeError as j_err:
        app.logger.error(f"Malformed json at path: {file_path} Error: {j_err}")
    return loaded_config

def get_all_routes(routes_dir="config/routes/"):
    '''
    Finds all the json files with within given directory
    that contain a "route" key
    args:
        (str): the directory to look for route configs. Default = config/routes/
    returns:
        (list of str): all of the route rules found
    '''
    route_path = os.path.join(app.instance_path, routes_dir)
    routes = []
    try:
        for conf_file in [os.path.join(route_path, j) for j in os.listdir(route_path) if j.endswith(".json")]:
            data = load_json_config(conf_file)
            if "route" in data:
                if isinstance(data["route"],list):
                    for r in data["route"]:
                        routes.append(r)
                else:
                    routes.append(data["route"])
    except FileNotFoundError as f_err:
        app.logger.warning(f"Route dir not found at path {route_path} - will use welcome home page route. Error: {f_err}")

    # if no routes are found, add a default one for the home page
    if not routes:
        routes.append("/")

    # prefer most specifc path (hardcoded path over variable) in left to right manner
    re_var = re.compile(r'<\w+:\w+>')
    sort_routes = []
    for rule in routes:
        sort_routes.append( (rule, re_var.sub(' ', rule)) )
    sort_routes = sorted(sort_routes, key=operator.itemgetter(1), reverse=True)

    return [r[0] for r in sort_routes]

def load_route_config(route_rule, routes_dir="config/routes/"):
    '''
    Return the json data for the provided directory
    args:
        route_rule (str): the route rule to match to in the json configs (the `route` key)
        routes_dir (str): the path to look for route configs. Default = config/routes/
    returns:
        (dict): The loaded json of the matched route config
    '''
    route_path = os.path.join(app.instance_path, routes_dir)
    data = OrderedDict()
    try:
        for conf_file in [os.path.join(route_path, j) for j in os.listdir(route_path) if j.endswith(".json")]:
            data = load_json_config(conf_file)
            if "route" in data:
                if isinstance(data["route"],list):
                    if route_rule in data["route"]:
                        break
                else:
                    if data["route"] == route_rule:
                        break
    except FileNotFoundError as f_err:
        app.logger.error(f"Route dir not found at path {route_path} - creating welcome home page route. Error: {f_err}")
        # if the base path (/) is used, provide a route config for the default home template
        data = OrderedDict({
            "route": ["/"],
            "template": "home.html.j2"
        })
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
    if not os.path.isdir(path):
        app.logger.warning(f"Failed to load json configs; invalid directory: {path}")
    for root, dirs, files in  os.walk(path):
        for config_file in files:
            if config_file.endswith('.json'):
                config_file_path = os.path.join(root, config_file)
                config_files[config_file_path] = load_json_config(config_file_path)
        if not recurse:
            break

    return config_files
