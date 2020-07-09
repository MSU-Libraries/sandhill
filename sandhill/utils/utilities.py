from sandhill import app

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
