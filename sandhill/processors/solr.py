from flask import request, jsonify
from urllib.parse import urlencode
from sandhill.utils.api import api_get
from sandhill import app

def query(data_dict):
    url = app.config['SOLR_BASE'] + "/select"

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
    # example url: /search?q=frogs&start=1&limit=10
    # example url: /search?q=frogs&result=json&start=1&rows=10
    # example url: /search?q=frogs AND Cows&start=1&rows=10
    # example url: /search?q=frogs&genre_aat="Theses"&page=1&start=1&rows=10
    # example url: /search?q=frogs&subject_display="Cooking"&subject_display="Menus"&page=1

    # use the request object to get the query and other params

    # Check if the query is empty 

    # Check for solr injections or encode the query 

    # get the list of return fields from the config

    # assemble solr params 
    '''
    solr_params = {
            "q": query,
            "fq": filter_query,
            "start": start_count,
            "rows": limit,
            "wt": "json",
            "fl": filter_fields,
            "sort": sort_query,
            "facet": "on",
            "facet.field": facet_fields,
            "facet.mincount": facet_mincount,
            "facet.limit": facet_limit,
            "qf": query_boost_fields
            }
    '''
    solr_params = {
            "q": "frogs",
            "start": 0,
            "rows": 10,
            "wt": "json",
            "defType": "dismax"
            }
    # make the solr call
    data_dict['params'] = solr_params
    search_results = query(data_dict)
    # check if the return type is HTML or JSON

    # return results 
    return jsonify(search_results)
