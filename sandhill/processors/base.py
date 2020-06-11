import re
import json
from . import solr
from . import json_file
from flask import request
from jinja2 import Template

def load_route_data(route_data):
    loaded_data = {}
    # add view_args into loaded_data
    loaded_data['view_arg'] = request.view_args

    for i in range(len(route_data)):
        # Apply Jinja2 templating to data config
        data_json = json.dumps(route_data[i])
        data_template = Template(data_json)
        data_json = data_template.render(**loaded_data)
        route_data[i] = json.loads(data_json)

        if route_data[i]['type'] == 'solr': 
            loaded_data[route_data[i]['name']] = solr.query_record(route_data[i])
        if route_data[i]['type'] == 'json_file':
            loaded_data[route_data[i]['name']] = json_file.load_file(route_data[i])

    return loaded_data
