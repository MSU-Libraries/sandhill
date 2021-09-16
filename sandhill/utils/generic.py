"""
Generic function that can be used in any context
"""
import os
import re
from collections import OrderedDict
from sandhill import app, catch

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
    if len(args) not in [2, 3]:
        raise TypeError(
            f"ifnone() missing required positional argument (2 or 3) {len(args)} received."
        )
    if len(args) == 3:
        key = args[1]
        default_val = args[2]
        return var[key] if isinstance(var, dict) and key in var else default_val # pylint: disable=unsupported-membership-test,unsubscriptable-object
    # len(args) == 2
    default_value = args[1]
    return var if var is not None else default_value

def combine_to_list(*args):
    """
    Combine a and b, which may be a scalar variable or list, and returns them as a list
    """
    combined = []
    for i in args:
        if isinstance(i, list):
            combined += i
        else:
            combined.append(i)
    return combined

def combine_to_unique_list(*args):
    """Remove duplicates from combined list."""
    unique_list = []
    _ = [unique_list.append(i) for i in combine_to_list(*args) if i not in unique_list]
    return unique_list

@catch(ValueError, "Could not find '{list_keys}' in: {obj}", return_val=None)
def get_descendant_from(obj, list_keys, extract=False):
    '''
    Gets key values from the dictionary/list if they exist;
    will check recursively through the obj
    args:
        obj (dict|list): Hierarchy of dict/lists to check
        list_keys (list|str): List of descendants to follow (or . delimited string)
        extract (bool): If set to true, will remove the last matching value
    returns:
        (any): The last matching value from list_keys, or None if no match
    '''
    if isinstance(list_keys, str):
        list_keys = list_keys.split('.')
    for idx, key in enumerate(list_keys):
        pobj = obj  # parent obj - used for extract
        if isinstance(obj, OrderedDict):
            obj = dict(obj)
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        elif isinstance(obj, list) and int(key) < len(obj):
            key = int(key)
            obj = obj[key]
        else:
            obj = None
        if extract and obj and (idx+1) == len(list_keys):
            del pobj[key]
    return obj if list_keys else None

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
    elif name in app.config and app.config[name] is not None:
        value = app.config[name]
    return value

def get_module_path(path):
    """
    Get the Python module path for a directory or file in Sandhill
    returns:
        (str): module (e.g. 'instance' or 'sandhill.test_instance.filters')
    """
    install_path = os.path.dirname(app.root_path)
    subpath = re.sub('^' + re.escape(install_path), '', path)
    return re.sub('\\.py$', '', subpath).strip('/').replace('/', '.')
