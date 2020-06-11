import re
from . import solr
from . import json_file
from flask import request

def load_data(data_dict, data):
    loaded_data = None
    data_dict = replace_params(data_dict, data)

    if data_dict and 'type' in data_dict and data_dict['type'] == 'solr': 
        loaded_data = solr.query_record(data_dict)
    if data_dict and 'type' in data_dict and data_dict['type'] == 'json_file':
        loaded_data = json_file.load_file(data_dict)

    return loaded_data

def replace_params(data_dict, data):
    '''
    do variable substitution in params values and data values
    '''
    for pk,pv in data_dict['params'].items():
        for rk,rv in request.view_args.items():
            data_dict['params'][pk] = data_dict['params'][pk].replace('<ARG.'+rk.upper()+'>', str(rv))
    for k, v in data_dict['params'].items():
        # check in our existing data for the variable name
        found = re.search('<([a-zA-Z]+)\.(\w+)\.?(\d*)>', v)
        if found:
            # check if that variable has the key mentioned in the config
            if found.group(1) in data and found.group(2) in data[found.group(1)]:
                val = data[found.group(1)][found.group(2)]
                # if the value is an array, get the index from the config
                if isinstance(val, list) and found.group(3) != '':
                    index = int(found.group(3))
                    val = val[index]
                # if the config key starts with 'path' then value has a non alphanumeric character in it, replace with '_'
                # this is to prevent filenames containing a slash or other weird characters in them
                val = re.sub("\W", "_", val) if k.startswith("path") else val
                data_dict['params'][k] = data_dict['params'][k].replace(found.group(0), str(val))

    return data_dict
