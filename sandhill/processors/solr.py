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
