import collections
from flask import request, render_template, abort
from flask import Response as FlaskResponse
from requests.models import Response as RequestsResponse
from jinja2.exceptions import TemplateNotFound
from sandhill import app
from sandhill.utils.decorators import add_routes
from sandhill.utils.generic import ifnone
from sandhill.utils.config_loader import load_route_config
from sandhill.processors.base import load_route_data


@add_routes()
def main(*args, **kwargs):
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
    return_val = None
    route_used = request.url_rule.rule
    ## loop over all the configs in the instance dir looking at the "route"
    ## field to determine which configs to use
    route_config = load_route_config(route_used)
    response_var = ifnone(route_config, 'response', None)
    ## process and load data routes
    data = {}
    route_data = []
    if 'data' in route_config:
        for idx, entry in enumerate(route_config['data']):
            if 'name' in entry and 'processor' in entry:
                route_data.append(entry)
            else:
                app.logger.warning("Unable to parse route data entry number {0} for: {1}"
                                   .format(idx,','.join(route_config['route'])))
        data = load_route_data(route_data)
    ## if a template is provided, render the tempate with the data
    if 'template' in route_config:
        return_val = handle_template(route_config['template'], response_var, **data)
    elif 'stream' in route_config:
        return_val = handle_stream(route_config['stream'], **data)
    else:
        # configs do not specify the minimum required data to load a page
        abort(404)

    return return_val

def handle_template(template, response_var, **data):
    try:
        if response_var in data and isinstance(data[response_var], FlaskResponse):
            return data[response_var]
        return render_template(template, **data)
    except TemplateNotFound:
        app.logger.warning("Could not find template to render: {0}".format(template))
        abort(501)

def handle_stream(stream_var, **data):
    allowed_headers = ['Content-Type', 'Content-Disposition', 'Content-Length']
    if stream_var not in data:
        abort(500)
    resp = data[stream_var]
    if isinstance(resp, RequestsResponse) and not resp:
        abort(resp.status_code)
    elif not resp:
        abort(503)

    stream = FlaskResponse(resp.iter_content(chunk_size=app.config['STREAM_CHUNK_SIZE']))
    for header in allowed_headers:
        if header in resp.headers.keys():
            stream.headers.set(header, resp.headers.get(header))
    return stream
