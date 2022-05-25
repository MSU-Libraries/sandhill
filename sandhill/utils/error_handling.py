'''
Methods to help handle errors
'''
import inspect
from typing import Any  # pylint: disable=unused-import
from functools import wraps
from flask import abort, request
import sandhill

def dp_abort(http_code):
    """
    Data processor abort. Will abort with the given status code if
    the data processor has an `on_fail` key set and the value is `0`.
    If the value is non-`0`, the 'on_fail' code will override
    the passed code.
    Args:
        http_code (int): A valid HTTP status code
    Raises:
        (HTTPException): Can raises exception if data processor's `on_fail` is
            defined in parent context
    """
    parent_locals = inspect.currentframe().f_back.f_locals
    data = parent_locals['data'] if 'data' in parent_locals else {}
    if 'on_fail' in data:
        abort(http_code if data['on_fail'] == 0 else data['on_fail'])

def catch(exc_class, exc_msg=None, **kwargs):
    """
    Decorator to catch general exceptions and handle in a standarized manor.
    Args:
        exc_class (Exception): Type of exception to catch
        exc_msg (String) (optional): Message to log; the
            parameter `{exc}` is available in the string template.\n
            Ex: `f"Error: {exc}"`
        **kwargs: Optional arguments:\n
            return_val (Any): Value to return after the exception has been handled\n
            return_arg (str): Function kwarg to be returned after the exception has been handled\n
            abort (int): Status code to abort with
    Returns:
        (Any): Only if return_val or return_arg is provided in kwargs.
    Raises:
        (HTTPException): If no return_val or return_arg is provided in kwargs.
    Examples:
    ```python
    @catch(KeyError, "Some error message", return_val=None)
    def myfunc():
        ...

    @catch((KeyError, IndexError), "Some error message", return_arg='myval')
    def myfunc(myval):
        ...
    ```
    """
    def inner(func):
        @wraps(func)
        def wrapper(*args, **func_kwargs):
            try:
                rval = func(*args, **func_kwargs)
            except exc_class as exc:
                def get_func_params():
                    '''Get original function parameters and their current values (including
                    defaults, if not passed)'''
                    func_params = {}
                    sig = inspect.signature(func)
                    for idx, (pname, param) in enumerate(sig.parameters.items()):
                        if pname not in func_params:
                            func_params[pname] = param.default
                        if idx < len(args):
                            func_params[pname] = args[idx]
                    return func_params

                # Re-map the function arguments to their variable name
                # for use in formatted error message string
                args_dict = {**get_func_params(), **func_kwargs}
                args_dict['exc'] = exc

                # Handling of the exception
                if exc_msg:
                    sandhill.app.logger.error(f"{request.url if request else ''} raised: " + \
                        exc_msg.format(**args_dict))

                # Get the return_arg value if required and present in the function's arguments
                return_arg = None
                if 'return_arg' in kwargs:
                    if kwargs.get('return_arg') and kwargs.get('return_arg') in args_dict:
                        return_arg = args_dict[kwargs.get('return_arg')]

                # Abort if specified
                if 'abort' in kwargs:
                    abort(kwargs.get('abort'))

                # If no return_val specified, we'll re-raise the error
                if 'return_val' not in kwargs and 'return_arg' not in kwargs:
                    raise exc
                rval = return_arg if return_arg else kwargs.get('return_val')
            return rval
        return wrapper
    return inner
