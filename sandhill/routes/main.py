import os
import collections
from flask import Flask, request, render_template, url_for, send_from_directory, Response, abort
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

    ## process and load data routes
    data = ()
    if 'data' in route_config:
        route_data = [d for d in route_config['data'] if 'name' in d and 'processor' in d]
        data = load_route_data(route_data)

    ## if a template is provided, render the tempate with the data
    if 'template' in route_config:
        try:
            return_val = render_template(route_config['template'], **data)
        except TemplateNotFound:
            abort(501) # not implemented
    elif 'stream' in route_config:
        resp = data[route_config['stream']]
        if resp:
            return_val =  Response(resp.iter_content(chunk_size=app.config['STREAM_CHUNK_SIZE']),
                                   content_type=resp.headers['Content-Type'])

    if not return_val:
        # TODO --  add route decorator to make custom error page
        abort(503) # service not available
    else:
        return return_val
            

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon') 
