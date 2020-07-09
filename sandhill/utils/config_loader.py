import os
import re
import collections
import json
from collections import OrderedDict

from .. import app

route_path = os.path.join(app.instance_path, "route_configs")

def get_all_routes():
    '''
    Finds all the json files with within /instance/route_configs
    that contain a "route" key
    '''
    routes = [] 
    var_counts = {}

    for conf_file in [os.path.join(route_path, j) for j in os.listdir(route_path) if j.endswith(".json")]:
        with open(conf_file,"r") as conf_data:
            data = json.load(open(conf_file,'r'))
            if "route" in data:
                if isinstance(data["route"],list):
                    for r in data["route"]:
                        routes.append(r)
                else:
                    routes.append(data["route"])

    # determine the number of variables in each route and add to dictionary
    for rule in routes:
        # re match to determine # of vars
        matches = re.findall('<\w+:\w+>', rule)
        var_counts[rule] = len(matches)

    # order the dictionary by lowest number of variables to greatest
    var_counts = sorted(var_counts.items(), key=lambda x: x[1])

    # return the list of the sorted routes
    return [r[0] for r in var_counts]

def load_route_config(route_rule):
    '''
    Return the json data for the provided route_config
    '''
    data = collections.OrderedDict()
    for conf_file in [os.path.join(route_path, j) for j in os.listdir(route_path) if j.endswith(".json")]:
        with open(conf_file,"r") as conf_data:
            data = json.load(conf_data, object_pairs_hook=collections.OrderedDict)
            if "route" in data:
                if isinstance(data["route"],list):
                    if route_rule in data["route"]:
                        break
                else:
                    if data["route"] == route_rule:
                        break
    return data

def load_search_config():
    """
    loads the search config file from instance/search/basic_search.json
    """
    search_config = collections.OrderedDict()
    search_config_path = os.path.join(app.instance_path, "search_configs/search.json")
    try:
        with open(search_config_path) as json_file:
            app.logger.info("loading json file at {0}".format(search_config_path))
            search_config = json.load(json_file, object_pairs_hook=collections.OrderedDict)
    except IOError as io_exe:
        app.logger.error("Unable open file at {0}".format(search_config_path))
        app.logger.error("An IOError has occured: {0}".format(io_exe))
    return search_config
