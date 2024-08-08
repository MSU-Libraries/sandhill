"""
Wrapper functions for JSONPath queries.
"""
import copy
import re
import json
from jsonpath_ng import parse
from jsonpath_ng.jsonpath import Fields, Index
from sandhill import app

def find(data, path=None, deepcopy=True):
    '''
    Get the values for a given JSONPath. \n
    Args:
        data (dict|list): The JSON data \n
        path (str): The JSONPath to find \n
    Returns:
        (list): A list of matches, empty if none found \n
    '''
    if deepcopy:
        data = copy.deepcopy(data)
    if path is None:
        return data
    pattern = parse(path)
    matches = pattern.find(data)
    return [match.value for match in matches]

def put(data, path, value, deepcopy=True):
    '''
    Set a value at the given JSONPath location. \n
    Args:
        data (dict|list): The JSON data \n
        path (str): The JSONPath to find \n
            Last element in path will be removed, which must be \
            a specific Field or Index only \n
        value (any): The value to set\n
    Returns:
        (dict|list): The modified JSON data \n
    '''
    if deepcopy:
        data = copy.deepcopy(data)
    pattern = parse(path)
    if not isinstance(pattern.right, Fields) and not isinstance(pattern.right, Index):
        raise ValueError("jsonpath.put can only set specific Fields or Indexes")

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
    Append a value to the given JSONPath location. Location must be a list. \n
    Args:
        data (dict|list): The JSON data \n
        path (str): The JSONPath to a list(s) \n
        value (any): The value to append \n
    Returns:
        (dict|list): The modified JSON data \n
    '''
    if deepcopy:
        data = copy.deepcopy(data)
    pattern = parse(path)
    matches = pattern.find(data)
    for match in matches:
        section = match.value
        if not isinstance(section, list):
            raise ValueError("jsonpath.append can only do so to a list. " \
                             f"Path '{path}' found type {type(section)}")
        section.append(value)
        parse(str(match.full_path)).update(data, section)
    return data

def delete(data, path, deepcopy=True):
    '''
    Delete item(s) from JSON data. \n
    Args:
        data (dict|list): The JSON data \n
        path (str): The JSONPath to the object(s) to delete \n
            Last element in path will be removed, which must be \
            a specific Field or Index only \n
    Returns:
        (dict|list): The modified JSON data \n
    '''
    if deepcopy:
        data = copy.deepcopy(data)
    pattern = parse(path)
    if not isinstance(pattern.right, Fields) and not isinstance(pattern.right, Index):
        raise ValueError("jsonpath.put can only set specific Fields or Indexes")

    matches = pattern.left.find(data)
    for match in matches:
        new_value = match.value
        idxs = [pattern.right.index] if isinstance(pattern.right, Index) \
            else pattern.right.reified_fields(match.context)
        for idx in idxs:
            del new_value[idx]
        parse(str(match.full_path)).update(data, new_value)

    return data

def eval_within(string: str, context: dict):
    '''
    Given a string containing JSONPath queries, replace the queries with the values they found.\n
    JSONPath queries will query within the context.\n
    **Example context** \n
    ```json
    {
        "item": {
            "elem1": { "elem2": "value1" } }
        "parent": {
            "elem3": "value2" }
    }
    ``` \n
    **Example query strings** \n
    ```python
    # No given context
    "$.elem1.elem2"     # would query the first item in the context dictionary
    # Specified conext
    "$parent.elem3"     # would query the the "parent" key in the context dictionary
    ``` \n
    Args:
        string (str): The string to search within for JSONPath queries \n
        context (dict): A dictionary of contexts upon which a JSONPath could query. \n
    '''
    if not isinstance(context, dict) or len(context) == 0:
        app.logger.debug("jsonpath.eval_within given invalid/empty context. Skipping.")
        return string

    space_esc = '&&&SPACE&&&'
    # find matching square brackets and replace spaces with placeholder
    brackets = re.findall(r'(\[.+?\])', string)
    for before, after in zip(brackets, [bkt.replace(' ', space_esc) for bkt in brackets]):
        string = string.replace(before, after, 1)

    parts = re.split(r'\s', string)

    # for vals starting with  $, JSONPath find and replace value with str() of result
    jsonpath_pat = re.compile(r'^\$([a-zA-Z0-9_]+)?\.([^ ]+)$')
    context_keys = list(context.keys())
    for idx, part in enumerate(parts):
        if (match := jsonpath_pat.match(part)):
            ctx_key = match.group(1)
            if not ctx_key:
                ctx_key = context_keys[0]
            path = f"$.{match.group(2)}".replace(space_esc, " ")
            result = find(context[ctx_key], path) if ctx_key in context else []
            # If only one results, then remove it from list
            result = result[0] if len(result) == 1 else result
            result = json.dumps(result) if isinstance(result, str) else result
            parts[idx] = result
        else:
            parts[idx] = part.replace(space_esc, " ")

    return " ".join([str(part) for part in parts])
