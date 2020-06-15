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
                if data["route"] == route_rule:
                    break
                
    return data
