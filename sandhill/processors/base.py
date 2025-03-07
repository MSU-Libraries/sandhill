'''
Base processor which handles loading of all other processors dynamically
so that additional processors can simply be added to this directory without
requiring code changes to load it.
'''
import json
from functools import cache
from importlib import import_module
from ast import literal_eval
from flask import request, abort, Response as FlaskResponse
from jinja2 import TemplateError
from werkzeug.wrappers.response import Response as WerkzeugReponse
from werkzeug.exceptions import HTTPException
from sandhill import app, catch
from sandhill.utils.template import render_template_json, render_template_string


def load_route_data(route_data):
    """
    Loop through route data, applying Jinja replacements \n
    and calling route data processors specified \n
    Args:
        route_data (list): Data loaded from the route config file \n
    Returns:
        (dict): The loaded data \n
    """
    loaded_data = {}
    # add view_args into loaded_data
    loaded_data['view_args'] = request.view_args
    for i, _ in enumerate(route_data):
        # Check when clause (if set) prior to attempting to render route processor
        if not eval_when(route_data[i], loaded_data):
            continue

        # Apply Jinja2 templating to data config
        try:
            route_data[i] = render_template_json(route_data[i], loaded_data)
        except json.JSONDecodeError:
            app.logger.warning("Unable to JSON decode route data. Possible bad request for: " \
                               f"{request.base_url}")
            abort(400)
        # Merging loaded data into route data, but route data takes precedence on a key conflict
        route_data[i] = {**loaded_data, **route_data[i]}

        # Dynamically load processor
        name, processor, action = identify_processor_components(route_data[i])

        # Identify action from within processor, if valid
        action_function = identify_processor_function(name, processor, action)

        # Call action from processor
        if action_function:
            try:
                loaded_data[name] = action_function(route_data[i])
            except HTTPException as exc:
                # Make abort calls abide by on_fail route setting
                if 'on_fail' in route_data[i]:
                    on_fail = int(route_data[i]['on_fail'])
                    exc_fail = exc.code if hasattr(exc, "code") else 503
                    on_fail = on_fail if on_fail != 0 else exc_fail
                    abort(on_fail)
        # Trigger abort with 'on_fail', if set; otherwise allow failure and continue
        if (name not in loaded_data or loaded_data[name] is None) and 'on_fail' in route_data[i]:
            app.logger.warning(
                f"Processor '{processor}' used for variable '{name}' returned "
                f"None and had on_fail value of '{route_data[i]['on_fail']}'")
            try:
                abort(int(route_data[i]['on_fail']))
            except ValueError:
                app.logger.error(f"Invalid on_fail set, must be int: {route_data[i]['on_fail']}")
                abort(500)

        # If the result from the processor is a Response, stop processing and return it
        if name in loaded_data and isinstance(loaded_data[name], (FlaskResponse, WerkzeugReponse)):
            return loaded_data[name]

    return loaded_data

def identify_processor_components(route_data):
    '''
    Get the processor name, function name, and variable name components \n
    Args:
        route_data (dict): has the keys of 'name' and 'processor' \n
    Returns:
        (tuple[str, str, str]): variable name, processor name, function name \n
    '''
    name = route_data['name']
    try:
        processor, action = route_data['processor'].rsplit('.', 1)
    except ValueError:
        app.logger.error(f"No 'action' set for processor: {route_data['processor']}")
        processor = route_data['processor']
        action = "no action defined"
    return name, processor, action

def identify_processor_function(name, processor, action):
    '''
    Verify we can load the function specified in the configs \n
    Args:
        name: variable name for the data process in the route_config \n
        processor: name of the processor module \n
        action: function within the processor to call \n
    Returns:
        function: loaded processor function \n
    '''
    action_function, load_exc = processor_load_action(
        f"instance.processors.{processor}",
        action)
    if not action_function:
        action_function, load_exc = processor_load_action(
            f"sandhill.processors.{processor}",
            action)
    if load_exc:
        app.logger.warning(f"Could not load action '{action}' from processor '{processor}'; "
                           f"skipping route data '{name}'."
                           f"Error: {load_exc}")
    return action_function

@cache
def processor_load_action(absolute_module, action):
    '''
    Attempt to get the action function from the provided module \n
    Args:
        absolute_module (str): Name of the module to load \n
        action (str): Function name within the module to load \n
    Returns:
        (tuple[func, Exception]): The loaded callable function; any exception \
                                  that occured while loading the function \n
    '''
    try:
        mod = import_module(absolute_module)
        action_function = getattr(mod, action)
        app.logger.debug(f"Successfully loaded processor action '{absolute_module}'")
        return action_function, None
    except (ImportError, AttributeError) as exc:
        return None, exc

@catch((ValueError, SyntaxError), "Could not literal_eval 'when' condition for " \
       "\"{route_data[name]}\": {route_data[when]}", abort=500)
def eval_when(route_data, loaded_data):
    '''
    Evaluate the 'when' key of a data processor to determine if that data processor \
    should be processed. \n
    Args:
        route_data (dict): a data processor entry \n
    Returns:
        (Any): The evaluation of the 'when' key \n
    '''
    # Default to processing if no 'when' provided
    when = True
    if 'when' in route_data:
        try:
            route_data['when'] = render_template_string(route_data['when'], loaded_data)
        except TemplateError:
            app.logger.warning(f"Unable to render 'when' clause for '{route_data['name']}' " \
                               f"(check syntax and values): {route_data['when']}")
            abort(500)
        when = literal_eval(route_data['when'])
    return when
