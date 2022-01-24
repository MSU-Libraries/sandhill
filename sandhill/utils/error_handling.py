'''
Methods to help handle errors
'''
import inspect
from functools import wraps
from flask import abort, request
import sandhill

def dp_abort(http_code):
    """
    Data processor abort. Will abort with the given status code if
    the data processor has an 'on_fail' key set and the value is 0.
    If the value is non-0, the 'on_fail' code will be override
    the passed code.
    args:
        http_code(int): A valid HTTP code
    throws:
        (HTTPException): Throws exception if data['on_fail'] is
            defined in parent context
    """
    parent_locals = inspect.currentframe().f_back.f_locals
    data = parent_locals['data'] if 'data' in parent_locals else {}
    if 'on_fail' in data:
        abort(http_code if data['on_fail'] == 0 else data['on_fail'])

def catch(exc_class, exc_msg=None, **kwargs):
    """
    Catch general exceptions and handle in a standarized manor
    args:
        exc_class(Exception): Type of exception to catch
        exc_msg(String) (optional): Message to log with the
            parameter {exc} available in the string template.
            Ex: f"Error: {exc}"
        kwargs:
            return_val(any): Value to return after the
                exception has been handled
            return_arg(String): Function kwarg to
                be returned after the exception has been handled
            abort(int): Status code to abort with
    returns:
        (any): If return_val or return_arg is provided in kwargs
    throws:
        (HTTPException): If no return_val or return_arg is provided in kwargs
    examples:
        @catch(KeyError, "Some error message", return_val=None)
        # where val is a kwarg to the func
        @catch((KeyError, IndexError), "Some error message", return_arg=val)
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
