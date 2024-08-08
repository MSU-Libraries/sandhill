'''
Processor for string functions
'''
from copy import deepcopy
import json
from requests import Response as RequestsResponse

def replace(data):
    '''
    For the given `name` in data, replace all occurances of an old string with new string and \
    return the result. \n
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `name` _str|requests.Response_: The context in which to find and replace.\n
            * `old` _str_: The string to find.\n
            * `new` _str_: The string to replace it with.\n
    Returns:
        (str|requests.Response|None): The same type as `data[name]` was, only now with string \
            replacements done. Or None if the 'name' value is None or missing. \n
    '''
    data_copy = deepcopy(data.get(data.get('name')))
    cont_copy = data_copy if data_copy is not None else ''

    # TODO able to handle regular string data (non-JSON)
    # TODO handle FlaskResponse as well
    if isinstance(data_copy, RequestsResponse):
        cont_copy = data_copy.text
    if cont_copy and not isinstance(cont_copy, str):
        cont_copy = json.dumps(cont_copy)
    cont_copy = cont_copy.replace(data['old'], data['new'])

    # pylint: disable=protected-access
    if isinstance(data_copy, RequestsResponse):
        data_copy._content = cont_copy.encode()
        data_copy.headers['Content-Length'] = len(data_copy._content)
    elif cont_copy:
        data_copy = json.loads(cont_copy)
    return data_copy
