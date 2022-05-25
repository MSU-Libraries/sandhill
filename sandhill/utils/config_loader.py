'''
Utilities for loading of loading `config/` files.
'''
import os
import re
import collections
import operator
import json
from json.decoder import JSONDecodeError
from sandhill import app, catch

@catch(OSError, "Unable to read json file at path: {file_path} Error: {exc}",
       return_val=collections.OrderedDict())
@catch(JSONDecodeError, "Malformed json at path: {file_path} Error: {exc}",
       return_val=collections.OrderedDict())
def load_json_config(file_path):
    """
    Load a JSON file.
    Args:
        file_path (str): The full path to the JSON file to load
    Returns:
        (dict): The contents of the loaded JSON file, or an empty dictionary
                upon error loading or parsing the file.
    """
    app.logger.info(f"Loading json file at {file_path}")
    with open(file_path, encoding='utf-8') as json_config_file:
        return json.load(json_config_file, object_pairs_hook=collections.OrderedDict)

@catch(FileNotFoundError, "Route dir not found at path {routes_dir} Error: {exc}", return_val=[])
def load_routes_from_configs(routes_dir="config/routes/"):
    '''
    Given a path relative to the `instance/` dir, load all JSON files within
    and extract the "route" keys.
    Args:
        routes_dir (string): The relative path to the JSON files
    Returns:
        (list): A list of routes from the configs
    '''
    route_path = os.path.join(app.instance_path, routes_dir)
    routes = []
    conf_files = [
        os.path.join(route_path, j) for j in os.listdir(route_path) if j.endswith(".json")
    ]
    for conf_file in conf_files:
        data = load_json_config(conf_file)
        if "route" in data:
            if isinstance(data["route"], list):
                for route in data["route"]:
                    routes.append(route)
            else:
                routes.append(data["route"])
    return routes

def get_all_routes(routes_dir="config/routes/"):
    '''
    Finds all routes in JSON files with within given directory and order them
    according to the desired load order.
    Args:
        routes_dir (str): The directory to look for route configs.
    Returns:
        (list): All of the route rules found in desired order.
    '''
    routes = load_routes_from_configs(routes_dir)

    # if no routes are found, add a default one for the home page
    if not routes:
        app.logger.warning("No routes loaded; will use welcome home page route.")
        routes.append("/")

    # prefer most specifc path (hardcoded path over variable) in left to right manner
    re_var = re.compile(r'<\w+:\w+>')
    sort_routes = []
    for rule in routes:
        sort_routes.append((rule, re_var.sub(' ', rule)))
    sort_routes = sorted(sort_routes, key=operator.itemgetter(1), reverse=True)

    return [r[0] for r in sort_routes]

@catch(FileNotFoundError, "Route dir not found at path {routes_dir} - " \
       "creating welcome home page route. Error: {exc}",
       return_val=collections.OrderedDict({
           "route": ["/"],
           "template": "home.html.j2"
       }))
def load_route_config(route_rule, routes_dir="config/routes/"):
    '''
    Return the json data for the provided directory.
    Args:
        route_rule (str): the route rule to match to in the json configs (the `route` key)
        routes_dir (str): the path to look for route configs. Default = config/routes/
    Returns:
        (OrderedDict): The loaded json of the matched route config, or empty dict if not found
    '''
    route_path = os.path.join(app.instance_path, routes_dir)
    data = collections.OrderedDict()
    conf_files = [
        os.path.join(route_path, j) for j in os.listdir(route_path) if j.endswith(".json")
    ]
    for conf_file in conf_files:
        check_data = load_json_config(conf_file)
        if "route" in check_data:
            if isinstance(check_data["route"], list):
                if route_rule in check_data["route"]:
                    data = check_data
                    break
            else:
                if check_data["route"] == route_rule:
                    data = check_data
                    break
    return data

def load_json_configs(path, recurse=False):
    """
    Loads all the config files in the provided path.
    Args:
        path (string): The directory path from which to load the config files.
        recurse (bool): If set to True, does a recursive walk into the path.
    Returns:
        (dict): Dictionary with keys of each file path and values of their loaded JSON.
    """
    config_files = {}
    if not os.path.isdir(path):
        app.logger.warning(f"Failed to load json configs; invalid directory: {path}")
    for root, _, files in os.walk(path):
        for config_file in files:
            if config_file.endswith('.json'):
                config_file_path = os.path.join(root, config_file)
                config_files[config_file_path] = load_json_config(config_file_path)
        if not recurse:
            break

    return config_files
