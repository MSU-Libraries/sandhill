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
    if isinstance(data_copy, RequestsResponse):
        data_copy = data_copy.text
    # TODO handle FlaskResponse as well

    if not isinstance(data_copy, str):
        data_copy = json.dumps(data_copy)
    data_copy = data_copy.replace(data_dict['old'], data_dict['new'])

    # pylint: disable=protected-access
    if isinstance(data_dict[data_dict['name']], RequestsResponse):
        data_dict[data_dict['name']]._content = data_copy.encode()
        data_dict[data_dict['name']].headers['Content-Length'] = \
            len(data_dict[data_dict['name']]._content)
    else:
        data_dict[data_dict['name']] = json.loads(data_copy)
    return data_dict[data_dict['name']]
