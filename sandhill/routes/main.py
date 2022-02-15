'''
Entry point for the web application
'''
from flask import request, abort, json, jsonify, Response as FlaskResponse
from werkzeug.wrappers.response import Response as WerkzeugReponse
from sandhill.utils.config_loader import load_route_config, get_all_routes
from sandhill.processors.base import load_route_data
from sandhill import app

def add_routes():
    """
    Decorator function for adding routes based on all
    json route configs in instance folder
    """
    app.logger.info("Running add_routes")
    def decorator(func, **options):
        all_routes = get_all_routes()
        app.logger.info(f"Loading routes: {', '.join(all_routes)}")
        for rule in all_routes:
            endpoint = options.pop('endpoint', None)
            app.logger.info(
                f"Adding URL rule: {rule}, {endpoint}, {func} {json.dumps(options)}"
            )
            app.add_url_rule(rule, endpoint, func, **options)
        return func
    return decorator

@add_routes()
def main(*args, **kwargs): # pylint: disable=unused-argument
    '''
    Entry point for the whole application, handling all routes and determining
    if it should render a template or stream a result.
    Based on the route_config that the path matches to, it will load all the
    required data processors before rendering the result.

    args/kwargs: all of the variables defined in the route configs
        ex: "/<string:namespace>/<int:id>" would have namespace and id passed in kwargs

    returns:
        Nothing, template is rendered or result is streamed
    '''
    route_used = request.url_rule.rule
    ## loop over all the configs in the instance dir looking at the "route"
    ## field to determine which configs to use
    route_config = load_route_config(route_used)
    ## process and load data routes
    route_data = []
    data = {}
    ## if 'template' is in the route_config, append the template processor
    ## to handle legacy configs
    if 'template' in route_config:
        if 'data' not in route_config:
            route_config['data'] = []
        route_config['data'].append(
            {
                'processor': 'template.render',
                'file': route_config['template'],
                'name': '_template_render'
            })
    if 'data' in route_config:
        for idx, entry in enumerate(route_config['data']):
            if 'name' in entry and 'processor' in entry:
                route_data.append(entry)
            else:
                app.logger.warning(f"Unable to parse route data entry number {idx} " \
                                   f"for: {1} {','.join(route_config['route'])}")
        data = load_route_data(route_data)
    # check if none of the route processors returned a FlaskResponse
    if not isinstance(data, (FlaskResponse, WerkzeugReponse)):
        app.logger.error(
            f"None of the 'data' processors in {route_config['route']}"
            f" returned a Response object"
        )
        if app.debug:
            data = jsonify(data)
        else:
            abort(500)
    return data
