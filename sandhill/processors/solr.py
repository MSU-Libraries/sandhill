from ..utils.api import api_get
from .. import app

def query(data_dict):
    url = app.config['SOLR_BASE'] + data_dict['base']

    # query solr with the parameters
    response = api_get(url, data_dict['params'])

    # convert to JSON
    return response.json()

def query_record(data_dict):
    json_data = query(data_dict)
    return json_data['response']['docs'][0]
