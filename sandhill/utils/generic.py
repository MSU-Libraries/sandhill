"""
Generic function that can be used in any context
"""

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
