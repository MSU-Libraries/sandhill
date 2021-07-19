import json
import copy
from jsonpath_ng import parse
from jsonpath_ng.jsonpath import Fields, Index

def set(data, path, value, deepcopy=True):
    '''
    Set a value at the given JSONPath location
    args:
        data (dict|list): The JSON data
        path (str): The JSONPath to find
            Last element in path will be removed, which must be
            a specific Field or Index only
        value (any): The value to set
    returns:
        (dict|list): The modified JSON data
    '''
    if deepcopy:
        data = copy.deepcopy(data)
    pattern = parse(path)
    matches = pattern.left.find(data)
    if not isinstance(pattern.right, Fields) and not isinstance(pattern.right, Index):
        raise ValueError("jsonpath.set can only set specific Fields or Indexes")
    for match in matches:
        new_value = match.value
        idxs = [pattern.right.index] if isinstance(pattern.right, Index) \
            else pattern.right.reified_fields(match.context)
        for idx in idxs:
            new_value[idx] = value
        parse(str(match.full_path)).update(data, new_value)

    return data

def delete(data, path, deepcopy=True):
    '''
    Delete item(s) from JSON data
    args:
        data (dict|list): The JSON data
        path (str): The JSONPath to the object(s) to delete
            Last element in path will be removed, which must be
            a specific Field or Index only
    returns:
        (dict|list): The modified JSON data
    '''
    if deepcopy:
        data = copy.deepcopy(data)
    pattern = parse(path)
    matches = pattern.find(data)
    for match in matches:
        parent_context = match.context
        if not isinstance(match.path, Fields) and not isinstance(match.path, Index):
            raise ValueError("jsonpath.delete can only delete specific Fields or Indexes")
        new_value = parent_context.value
        idxs = [match.path.index] if isinstance(match.path, Index) \
            else match.path.reified_fields(match.context)
        for idx in idxs:
            del new_value[idx]
        parse(str(parent_context.full_path)).update(data, new_value)

    return data
