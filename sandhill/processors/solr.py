from ..utils.api import api_get
from flask import request
from .. import app

def query(data_dict):
    url = app.config['SOLR_BASE'] + data_dict['base']
    # do variable substitution in params values
    for pk,pv in data_dict['params'].items():
        for rk,rv in request.view_args.items():
            #app.logger.info("View Arg: " + rk.upper() + "  (" + str(rv) + ")")
            data_dict['params'][pk] = data_dict['params'][pk].replace('<ARG.'+rk.upper()+'>', str(rv))

    response = api_get(url, data_dict['params'])
    # convert to JSON
    return response.json()

def query_record(data_dict):
    json_data = query(data_dict)
    return json_data['response']['docs'][0]
