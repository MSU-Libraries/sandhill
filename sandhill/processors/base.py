import json
from sandhill import app
from sandhill.utils.template import render_template
from flask import request, abort
from importlib import import_module

def load_route_data(route_data):
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
        name = route_data[i]['name']
        processor, action = route_data[i]['processor'].rsplit('.', 1)
        action_function = None
        try:
            mod = import_module("sandhill.processors." + processor)
            action_function = getattr(mod, action)
            app.logger.debug("Successfully loaded processor '{0}' and action '{1}'".format(processor, action))
        except (ImportError, AttributeError) as exc:
            #TODO log the exc
            app.logger.warning("Could not load action '{0}' from processor '{1}'; "
                               "skipping route data '{2}'.".format(action ,processor, name))

        if action_function:
            loaded_data[name] = action_function(route_data[i])

        if (name not in loaded_data or loaded_data[name] is None) and 'on_fail' in route_data[i]:
            app.logger.error("Could not load data for processor '{0}' used for variable '{1}'".format(processor, name))
            abort(int(route_data[i]['on_fail']))

    return loaded_data
