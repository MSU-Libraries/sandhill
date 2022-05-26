'''
Processor for string functions
'''
import json
from requests import Response as RequestsResponse

def replace(data):
    '''
    For the given `name` in data, replace all occurances of an old string with new string and \
    return the result.
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `name` _str|requests.Response_: The context in which to find and replace.\n
            * `old` _str_: The string to find.\n
            * `new` _str_: The string to replace it with.\n
    Returns:
        (str|requests.Response): The same type as `data[name]` was, only now with string \
            replacements done.
    '''
    data_copy = data[data['name']]
    # TODO able to handle regular string data (non-JSON)
    if isinstance(data_copy, RequestsResponse):
        data_copy = data_copy.text
    # TODO handle FlaskResponse as well

    if not isinstance(data_copy, str):
        data_copy = json.dumps(data_copy)
    data_copy = data_copy.replace(data['old'], data['new'])

    # pylint: disable=protected-access
    if isinstance(data[data['name']], RequestsResponse):
        data[data['name']]._content = data_copy.encode()
        data[data['name']].headers['Content-Length'] = \
            len(data[data['name']]._content)
    else:
        data[data['name']] = json.loads(data_copy)
    return data[data['name']]
