"""
Generic functions that could be used in most any context.
"""
import os
import re
from typing import Any  # pylint: disable=unused-import
from collections.abc import Mapping, Hashable
from sandhill import app, catch

def ifnone(*args):
    '''
    Returns the default value if the key is not in the dictionary or if
    a non-dictionary is provided it will return the default if it is not set.
    Args:
        *args:
            With 3 args:\n
                var (dict): The dictionary to check\n
                key (str): The key of the dictionary\n
                default_value: Return val if key is not in var\n
            With 2 args:\n
                var: The variable to check\n
                default_value: Return val if the variable is None\n
    Returns:
        The default_value if the value is None or the key is not in the dict.
    Raises:
        (TypeError): If invalid number of arguments passed.
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

def tolist(*args):
    """
    Combine arguments, appending them to a list; args may be scalars or lists. If args is
    a list, then the values of the list are appended (not the list itself).
    Args:
        *args: Items to combine.
    Returns
        (list): The combined list.
    """
    combined = []
    for i in args:
        if isinstance(i, list):
            combined += i
        else:
            combined.append(i)
    return combined

def touniquelist(*args):
    """
    Combine arguments while excluding duplicate values. Same functionality as `tolist()`
    only with duplicate values being removed.
    Args:
        *args: Items to combine.
    Returns
        (list): The combined list with duplicates removed.
    """
    unique_list = []
    _ = [unique_list.append(i) for i in tolist(*args) if i not in unique_list]
    return unique_list

@catch(ValueError, "Could not find {list_keys} in: {obj}", return_val=None)
def getdescendant(obj, list_keys, extract=False, put=None):
    '''
    Gets key values from the dictionary/list if they exist;
    will check recursively through the `obj`.
    Args:
        obj (dict|list): A dict/list to check, possibly containing nested dicts/lists.
        list_keys (list|str): List of descendants to follow (or . delimited string)
        extract (bool): If set to true, will remove the last matching value from the `obj`.
        put (Any): Replace the found value with this new value in the `obj`,
                   or append if the found value at a list key of `"[]"`
    Returns:
        (Any): The last matching value from list_keys, or None if no match
    Raises:
        IndexError: When attempting to put a list index that is invalid.
    Examples:
    ```python
    # Get "key1" of mydict, then index 2 of that result, then "key3" of that result
    v = getdescendant(mydict, "key1.2.key3")
    # Same as above, only also remove the found item from mydict
    v = getdescendant(mydict, "key1.2.key3", extract=True)
    # Replace value with new value
    v = getdescendant(mydict, "key1.2.key3", put="Replacement value!")
    # Append to a list
    v = getdescendant(mydict, "key1.2.[]", put="Append this value.")
    ```
    '''
    list_keys = list_keys.split('.') if isinstance(list_keys, str) else list_keys
    for idx, key in enumerate(list_keys):
        pobj = obj
        if isinstance(obj, Mapping) and key in obj:
            obj = obj[key]
        elif isinstance(obj, list) and str(key).isdigit() and int(key) < len(obj):
            key = int(key)
            obj = obj[key]
        else:
            obj = None
        #  This is the last key in the loop
        if (idx + 1) == len(list_keys):
            if extract and obj is not None:
                del pobj[key]
            if put is not None and pobj is not None:
                if isinstance(pobj, Mapping):
                    pobj[key] = put
                if isinstance(pobj, list):
                    if key == "[]":
                        pobj.append(put)
                    elif isinstance(key, int) and key < len(pobj):
                        pobj[key] = put
                    else:
                        raise IndexError(f"Index of {key} is invalid for list: {pobj}")
    return obj if list_keys else None

def getconfig(name, default=None):
    '''
    Get the value of the given config name. It will first
    check in the environment for the variable name, otherwise
    look in the app.config, otherwise use the default param
    Args:
        name (str): Name of the config variable to look for
        default (str|None): The defaut value if not found elsewhere
    Returns:
        (str): Value of the config variable, default value otherwise
    '''
    value = default
    if name in os.environ and os.environ[name]:
        value = os.environ[name]
    elif name in app.config and app.config[name] is not None:
        value = app.config[name]
    return value

def getmodulepath(path):
    """
    Get the Python module path for a directory or file in Sandhill
    Args:
        path (str): A file or dir path in Sandhill
    Returns:
        (str): module (e.g. 'instance' or 'sandhill.filters.filters')
    """
    install_path = os.path.dirname(app.root_path)
    subpath = re.sub('^' + re.escape(install_path), '', path)
    return re.sub('\\.py$', '', subpath).strip('/').replace('/', '.')

def pop_dict_matching_key(haystack: list[dict], match: dict, key: Hashable) -> list[dict]:
    """
    Search the haystack for all dicts that have the same
    value as the passed match dict for the given key.
    Matched dicts are removed from the haystack and
    returned as a list.
    Args:
        haystack (list): A list of dicts to search through.
        match (dict): The dict to match against.
        key (Hashable): The key (both dicts) for the comparison value.
    Returns:
        (list): A list of matching dicts removed from the haystack.
    """
    matched = []
    if (needle_val := match.get(key)):
        for hay in list(haystack):
            if hay.get(key) == needle_val:
                matched.append(hay)
                haystack.remove(hay)
    return matched

def overlay_dicts_matching_key(target: list[dict], overlays: list[dict], key: Hashable):
    """
    Given the target, find and replace matching dicts, for all matching dicts
    in the list of overlays, using the value for the provided key to compare them.
    For each overlay dict, overlay the values on top of any matching original
    dict from the target.
    If multiple overlays match an original target dict, both overlays will use
    the original dict as a base for the overlay.
    If no matching dict was found in the original target list, the overlay will be
    appended to the target as is.
    Args:
        haystack (list): The list of dicts to search and update.
        match (list): The list of dict match and overlay.
        key (Hashable): The key (both dicts) for the comparison value.
    Returns:
        (None)
    """
    base_ref = {}
    # Extract all base/default dictionaries from target
    for overlay in overlays:
        if (oval := overlay.get(key)):
            if [base_dict := tdict for tdict in target if tdict.get(key) == oval]:
                target.remove(base_dict)
                base_ref[oval] = base_dict

    # For each overlay, copy matching base and update with overlay before appending
    for overlay in overlays:
        if (base_dict := base_ref.get(overlay.get(key))):
            overlay = {**base_dict, **overlay}
        target.append(overlay)
