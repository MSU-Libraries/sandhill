"""
Generic function that can be used in any context
"""

def ifnone(var, key, default_val):
    '''
    Returns var[key] if key in var else the default_val
    '''
    return var[key] if isinstance(var, dict) and key in var else default_val

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
