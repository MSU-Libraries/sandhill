from ..utils.api import api_get
from .. import app

def query(data_dict):
    url = app.config['SOLR_BASE'] + "/select"

    # query solr with the parameters
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
