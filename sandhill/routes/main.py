import os
import collections
from flask import Flask, request, render_template, url_for, send_from_directory, Response, abort, wrappers
from jinja2.exceptions import TemplateNotFound
from .. import app
from ..utils.decorators import add_routes
from ..utils.config_loader import load_route_config
from ..processors.base import load_route_data


@add_routes()
def main(*args, **kwargs):
    return_val = None
    route_used = request.url_rule.rule
    
    ## loop over all the configs in the instance dir looking at the "route"
    ## field to determine which configs to use
    route_config = load_route_config(route_used)
    response_var = route_config['response'] if 'response' in route_config else None 

    ## process and load data routes
    data = {}
    if 'data' in route_config:
        route_data = [d for d in route_config['data'] if 'name' in d and 'processor' in d]
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
        print(response_var)
        print(data)
        if response_var in data:
            return data[response_var]
        return render_template(template, **data)
    except TemplateNotFound:
        abort(501) # not implemented

def handle_stream(stream_var, **data):
    allowed_headers = ['Content-Type', 'Content-Disposition', 'Content-Length']
    resp = data[stream_var]
    if not resp:
        abort(503) # service not available

    stream = Response(resp.iter_content(chunk_size=app.config['STREAM_CHUNK_SIZE']))
    for header in allowed_headers:
        if header in resp.headers.keys():
            stream.headers.set(header, resp.headers.get(header))
    return stream

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon') 
