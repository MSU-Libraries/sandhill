import os
import collections
from flask import json
from .. import app

def load_json(data_dict):
    file_data = collections.OrderedDict()

    # loop over each provided path and stop when one is found
    if 'paths' in data_dict:
        for path in data_dict['paths']:
            full_path = os.path.join(app.instance_path, path)
            if os.path.exists(full_path):
               file_data = json.load(open(full_path), object_pairs_hook=collections.OrderedDict)
               break

    return file_data
