import os
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
    for conf_file in [os.path.join(route_path, j) for j in os.listdir(route_path) if j.endswith(".json")]:
        with open(conf_file,"r") as conf_data:
            data = json.load(open(conf_file,'r'))
            if "route" in data:
                routes.append(data["route"])
    return routes

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
