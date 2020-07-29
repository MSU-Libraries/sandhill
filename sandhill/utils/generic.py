"""
Generic function that can be used in any context
"""

def ifnone(var, default_val):
    '''
    Returns var if it is not None else the default_val
    '''
    return var if var else default_val

def ifnone(var, key, default_val):
    '''
    Returns var[key] if key in var else the default_val
    '''
    return var[key] if key in var else default_val

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

