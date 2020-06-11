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
        for dck,dcv in data.items():
            for dk, dv in dcv.items():
                # if the data values is a list, use the first element, else convert to string
                val = dv[0] if isinstance(dv, list) and dv and len(dv) > 0 else str(dv)
                # if the pk is 'path' then value has a '/' in it, replace with '_'
                # this is to prevent filenames containing a slash in them
                val = val.replace("/","_") if pk.startswith("path") else val
                data_dict['params'][pk] = data_dict['params'][pk].replace('<ARG.'+dk+'>', str(val))
    return data_dict
