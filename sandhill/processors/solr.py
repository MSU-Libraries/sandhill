import os
from flask import request, jsonify, abort
from urllib.parse import urlencode, urljoin
from sandhill.utils.api import api_get
from sandhill import app
from sandhill.utils.config_loader import load_search_config
from sandhill.utils.generic import combine_to_list


def query(data_dict):
    url = os.environ.get('SOLR_URL') + "/select"

    # query solr with the parameters
    app.logger.debug("Connecting to {0}?{1}".format(url, urlencode(data_dict['params'])))
    response = api_get(url=url, params=data_dict['params'])

    # convert to JSON
    return response.json()

def query_record(data_dict):
    json_data = query(data_dict)
    if 'error' in json_data:
        app.logger.error(json_data['error'])
    elif json_data['response']['docs']:
        return json_data['response']['docs'][0]
    return None

def search(data_dict):
    """Searches solr and gets the results
        args:
        data_dict (dict) :  dictionary of url args
    """
    if 'config' not in data_dict:
        app.logger.error("Missing 'config' setting for processor '{0}' with name '{1}'".format(data_dict['processor'], data_dict['name']))
        abort(500)
    search_config = load_search_config(data_dict['config'])
    if 'solr_params' not in search_config:
        app.logger.error("Missing 'solr_params' inside search config file '{0}'".format(data_dict['config']))
        abort(500)

    search_params = request.args.to_dict(flat=False)
    solr_config = search_config['solr_params']
    solr_params = {}
    for field_name, field_conf in solr_config.items():
        solr_params[field_name] = []
        # Load base from config
        if 'base' in field_conf:
            solr_params[field_name] = field_conf['base']
        # Load from search_params if field defined with a default
        if field_name in search_params and 'default' in field_conf:
            solr_params[field_name] = combine_to_list(solr_params[field_name], search_params[field_name])
        # Load default from config if solr_param field not defined
        elif 'default' in field_conf:
            solr_params[field_name] = combine_to_list(solr_params[field_name], field_conf['default'])
        # Remove field from solr query if empty
        if not any(solr_params[field_name]):
            del solr_params[field_name]

        # restrictions
        #TODO something like: solr_params[field_name] = apply_restrictions(solr_params[field_name], field_conf['restrictions'])
        if 'max' in field_conf:
            solr_params[field_name] = [ val if str(val).isdigit() and int(val) < int(field_conf['max']) else field_conf['max'] for val in solr_params[field_name] ]
        if 'min' in field_conf:
            solr_params[field_name] = [ val if str(val).isdigit() and int(val) > int(field_conf['min']) else field_conf['min'] for val in solr_params[field_name] ]

    # make the solr call
    data_dict['params'] = solr_params
    return jsonify(query(data_dict))
