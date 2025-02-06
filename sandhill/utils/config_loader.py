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
from sandhill.utils.generic import tolist, tolistfromkeys
from sandhill.modules.routing import Route

@catch(OSError, "Unable to read json file at path: {file_path} Error: {exc}",
       return_val=collections.OrderedDict())
@catch(JSONDecodeError, "Malformed json at path: {file_path} Error: {exc}",
       return_val=collections.OrderedDict())
def load_json_config(file_path):
    """
    Load a JSON file. \n
    Args:
        file_path (str): The full path to the JSON file to load \n
    Returns:
        (dict): The contents of the loaded JSON file, or an empty dictionary \
                upon error loading or parsing the file. \n
    """
    app.logger.debug(f"Loading json file at {file_path}")
    with open(file_path, encoding='utf-8') as json_config_file:
        return json.load(json_config_file, object_pairs_hook=collections.OrderedDict)

@catch(FileNotFoundError, "Route dir not found at path {routes_dir} Error: {exc}", return_val=[])
def load_routes_from_configs(routes_dir="config/routes/"):
    '''
    Given a path relative to the `instance/` dir, load all JSON files within \
    and extract the "route" keys. \n
    Args:
        routes_dir (string): The relative path to the JSON files \n
    Returns:
        (list): A list of routes from the configs \n
    '''
    route_path = os.path.join(app.instance_path, routes_dir)
    routes = []
    conf_files = [
        os.path.join(route_path, j) for j in os.listdir(route_path) if j.endswith(".json")
    ]
    for conf_file in conf_files:
        data = load_json_config(conf_file)
        r_rules = tolist(*[data.get(key) for key in ("route", "routes") if key in data])
        methods = tolist(*[data.get(key) for key in ("method", "methods") if key in data])
        for rule in r_rules:
            routes.append(Route(
                rule=rule,
                methods=methods,
            ))
    return routes

def get_all_routes(routes_dir="config/routes/"):
    '''
    Finds all routes in JSON files with within given directory and order them \
    according to the desired load order. \n
    Args:
        routes_dir (str): The directory to look for route configs. \n
    Returns:
        (list): All of the route rules found in desired order. \n
    '''
    routes = load_routes_from_configs(routes_dir)

    # if no routes are found, add a default one for the home page
    if not routes:
        app.logger.warning("No routes loaded; will use welcome home page route.")
        routes.append(Route(rule="/"))

    # prefer most specifc path (hardcoded path over variable) in left to right manner
    re_var = re.compile(r'<\w+:\w+>')
    sort_routes = []
    for route in routes:
        sort_routes.append((route, re_var.sub(' ', route.rule)))
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
    Return the json data for the provided directory. \n
    Args:
        route_rule (str): the route rule to match to in the json configs (the `route` key) \n
        routes_dir (str): the path to look for route configs. Default = config/routes/ \n
    Returns:
        (OrderedDict): The loaded json of the matched route config, or empty dict if not found \n
    '''
    route_path = os.path.join(app.instance_path, routes_dir)
    data = collections.OrderedDict()
    conf_files = [
        os.path.join(route_path, j) for j in os.listdir(route_path) if j.endswith(".json")
    ]
    for conf_file in conf_files:
        check_data = load_json_config(conf_file)
        if route_rule in tolistfromkeys(check_data, "route", "routes"):
            data = check_data
            break
    return data

def load_json_configs(path, recurse=False):
    """
    Loads all the config files in the provided path. \n
    Args:
        path (string): The directory path from which to load the config files. \n
        recurse (bool): If set to True, does a recursive walk into the path. \n
    Returns:
        (dict): Dictionary with keys of each file path and values of their loaded JSON. \n
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
