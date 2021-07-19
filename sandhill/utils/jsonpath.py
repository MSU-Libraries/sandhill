import json
import copy
from jsonpath_ng import parse
from jsonpath_ng.jsonpath import Fields, Index

def find(data, path, deepcopy=True):
    '''
    Get the values for a given JSONPath
    args:
        data (dict|list): The JSON data
        path (str): The JSONPath to find
    returns:
        (list): A list of matches, empty if none found
    '''
    if deepcopy:
        data = copy.deepcopy(data)
    pattern = parse(path)
    matches = pattern.find(data)
    return [match.value for match in matches]

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
    if not isinstance(pattern.right, Fields) and not isinstance(pattern.right, Index):
        raise ValueError("jsonpath.set can only set specific Fields or Indexes")

    matches = pattern.left.find(data)
    for match in matches:
        new_value = match.value
        idxs = [pattern.right.index] if isinstance(pattern.right, Index) \
            else pattern.right.reified_fields(match.context)
        for idx in idxs:
            new_value[idx] = value
        parse(str(match.full_path)).update(data, new_value)

    return data

def append(data, path, value, deepcopy=True):
    '''
    Append a value to the given JSONPath location. Location must be a list.
    args:
        data (dict|list): The JSON data
        path (str): The JSONPath to a list(s)
        value (any): The value to append
    returns:
        (dict|list): The modified JSON data
    '''
    if deepcopy:
        data = copy.deepcopy(data)
    pattern = parse(path)
    matches = pattern.find(data)
    for match in matches:
        section = match.value
        if not isinstance(section, list):
            raise ValueError(f"jsonpath.append can only do so to a list. Path '{path}' found type {type(section)}")
        section.append(value)
        parse(str(match.full_path)).update(data, section)
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
    if not isinstance(pattern.right, Fields) and not isinstance(pattern.right, Index):
        raise ValueError("jsonpath.set can only set specific Fields or Indexes")

    matches = pattern.left.find(data)
    for match in matches:
        new_value = match.value
        idxs = [pattern.right.index] if isinstance(pattern.right, Index) \
            else pattern.right.reified_fields(match.context)
        for idx in idxs:
            del new_value[idx]
        parse(str(match.full_path)).update(data, new_value)

    return data
