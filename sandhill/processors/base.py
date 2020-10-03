'''
Base processor which handles loading of all other processors dynamically
so that additional processors can simply be added to this directory without
requiring code changes to load it.
'''
import json
from importlib import import_module
from flask import request, abort
from sandhill import app
from sandhill.utils.template import render_template

def load_route_data(route_data):
    """Loop through route data, applying Jinja replacements
    and calling route data processors specified
    args:
        route_data (list of OrderedDict): data loaded from the route config file
    return:
        dict containing loaded data
    """
    loaded_data = {}
    # add view_args into loaded_data
    loaded_data['view_args'] = request.view_args
    for i, _ in enumerate(route_data):
        # Apply Jinja2 templating to data config
        data_json = json.dumps(route_data[i])
        data_json = render_template(data_json, loaded_data)
        route_data[i] = json.loads(data_json)
        # Merging loaded data into route data, but route data takes precedence on a key conflict
        route_data[i] = {**loaded_data, **route_data[i]}

        # Dynamically load processor
        name, processor, action = _identify_processor_components(route_data[i])

        # Identify action from within processor, if valid
        action_function = _identify_processor_function(name, processor, action)

        # Call action from processor
        if action_function:
            loaded_data[name] = action_function(route_data[i])
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

    return loaded_data


def _identify_processor_components(route_data):
    '''
    Will get the processor name, function name, and variable name components
    args:
        route_data(dict): has the keys of 'name' and 'processor'
    returns:
        tuple<str, str, str>: variable name, processor name, function name
    '''
    name = route_data['name']
    try:
        processor, action = route_data['processor'].rsplit('.', 1)
    except ValueError:
        app.logger.error("No 'action' set for processor: {0}".format(route_data['processor']))
        processor = route_data['processor']
        action = "no action defined"
    return name, processor, action


def _identify_processor_function(name, processor, action):
    '''
    Verify we can load the function specified in the configs
    args:
        name: variable name for the data process in the route_config
        processor: name of the processor module
        action: function within the processor to call
    returns:
        function: loaded processor function
    '''
    action_function = None
    try:
        mod = import_module("sandhill.processors." + processor)
        action_function = getattr(mod, action)
        app.logger.debug(f"Successfully loaded processor '{processor}' and action '{action}'")
    except (ImportError, AttributeError) as exc:
        app.logger.warning(f"Could not load action '{action}' from processor '{processor}'; "
                           f"skipping route data '{name}'."
                           f"Error: {exc}")
    return action_function
