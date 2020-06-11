import os
import collections
from flask import json
from .. import app

def load_file(data_dict):
    file_data = collections.OrderedDict() 

    # loop over each provided path and stop when one is found
    if 'params' in data_dict:
        for jk, jv in data_dict['params'].items():
            full_path = os.path.join(app.instance_path, jv)
            if os.path.exists(full_path):
               file_data = json.load(open(full_path), object_pairs_hook=collections.OrderedDict)
               break

    return file_data
