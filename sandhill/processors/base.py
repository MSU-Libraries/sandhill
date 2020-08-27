import json
from sandhill import app
from sandhill.utils.template import render_template
from sandhill.utils.generic import ifnone
from flask import request, abort
from importlib import import_module

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
    for i in range(len(route_data)):
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
            app.logger.warning("Processor '{0}' used for variable '{1}' returned None and had on_fail value of '{2}'".format(
                processor, name, route_data[i]['on_fail']))
            try:
                abort(int(route_data[i]['on_fail']))
            except ValueError as exc:
                app.logger.error("Invalid on_fail set, must be integer: {0}".format(route_data[i]['on_fail']))
                abort(500)

    return loaded_data


def _identify_processor_components(route_data):
    name = route_data['name']
    try:
        processor, action = route_data['processor'].rsplit('.', 1)
    except ValueError as exc:
        app.logger.error("No 'action' set for processor: {0}".format(route_data['processor']))
        processor = route_data['processor']
        action = "no action defined"
    return name, processor, action


def _identify_processor_function(name, processor, action):
    action_function = None
    try:
        mod = import_module("sandhill.processors." + processor)
        action_function = getattr(mod, action)
        app.logger.debug("Successfully loaded processor '{0}' and action '{1}'".format(processor, action))
    except (ImportError, AttributeError) as exc:
        #TODO log the exc
        app.logger.warning("Could not load action '{0}' from processor '{1}'; "
                           "skipping route data '{2}'.".format(action ,processor, name))
        print(exc)
    return action_function

