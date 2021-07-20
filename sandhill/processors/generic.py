'''
Processor for generic functions
'''
import json
from requests import Response as RequestsResponse

def replace(data_dict):
    '''
    For the given 'name' in data, replace all occurances of an old string with new string
    args:
        data_dict(dict): Dict with 'old' and 'new' keys
    returns:
        dict: The updated data for the 'name' variable
    '''
    data_copy = data_dict[data_dict['name']]
    # TODO able to handle regular string data (non-JSON)
    if 'application/json' not in data_copy.headers.get('Content-Type'):
        return None

    if isinstance(data_copy, RequestsResponse) and \
      'application/json' in data_copy.headers.get('Content-Type'):
        data_copy = data_copy.json()
    # TODO handle FlaskResponse as well

    new_data = json.dumps(data_copy)
    new_data = new_data.replace(data_dict['old'], data_dict['new'])

    # pylint: disable=protected-access
    if isinstance(data_dict[data_dict['name']], RequestsResponse):
        data_dict[data_dict['name']]._content = new_data.encode()
        data_dict[data_dict['name']].headers['Content-Length'] = \
            len(data_dict[data_dict['name']]._content)
    else:
        data_dict[data_dict['name']] = json.loads(new_data)
    return data_dict[data_dict['name']]
