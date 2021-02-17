"""
Generic function that can be used in any context
"""
import os
from sandhill import app

def ifnone(*args):
    '''
    Returns the default value if the key is not in the dictionary or if
    a non-dictionary is provided it will return the default if it is not set.
    args:
        var (dict): The dictionary to check
        key (str): The key of the dictionary
        default_value: What to return if key is not in var
        OR
        var: The variable to check
        default_value: What to return if the variable is None
    Returns:
        The default_value if the value is None or the key is not in the dict
    Trows:
        TypeError
    '''
    var = args[0] if args else None
    if len(args) == 3:
        key = args[1]
        default_val = args[2]
        return var[key] if isinstance(var, dict) and key in var else default_val
    elif len(args) == 2:
        default_value = args[1]
        return var if var is not None else default_value
    else:
        raise TypeError(f"ifnone() missing required positional argument (2 or 3) {len(args)} received.")

def combine_to_list(*args):
    """
    Combine a and b, which may be a scalar variable or list, and returns them as a list
    """
    combined = []
    for x in args:
        if isinstance(x, list):
            combined += x
        else:
            combined.append(x)
    return combined

def combine_to_unique_list(*args):
    """Remove duplicates from combined list."""
    unique_list = []
    [unique_list.append(x) for x in combine_to_list(*args) if x not in unique_list]
    return unique_list

def get_descendant_from_dict(dict_obj, list_keys):
    '''
    Gets key values from the dictionary if they exist
    which will check recursively through the dict_obj
    args:
        dict_obj (dict): Dictionary of the tree to check
        list_keys (list): List of descendants to follow
    '''
    for key in list_keys:
        if isinstance(dict_obj, dict) and key in dict_obj:
            dict_obj = dict_obj[key]
        else:
            dict_obj = None
    return dict_obj if list_keys else None

def get_config(name, default=None):
    '''
    Get the value of the given config name. It will first
    check in the environment for the variable name, otherwise
    look in the app.config, otherwise use the default param
    args:
        name (str): Name of the config variable to look for
        default(str/None): The defaut value if not found elsewhere
    returns:
        (str): Value of the config variable, default value otherwise
    '''
    value = default
    if name in os.environ and os.environ[name]:
        value = os.environ[name]
    elif name in app.config:
        value = app.config[name]
    return value
