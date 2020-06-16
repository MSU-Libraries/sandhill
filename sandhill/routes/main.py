import os
import collections
from flask import Flask, request, render_template, url_for, send_from_directory, Response
from .. import app
from ..utils.decorators import add_routes
from ..utils.config_loader import load_route_config
from ..processors.base import load_route_data


@add_routes()
def main(*args, **kwargs):
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
        return render_template(route_config['template'], **data)
    else: ## else, stream results
        # Get the the non view_arg data -- TODO is there a cleaner way to do this part?
        resp = data[[k for k,v in data.items() if k != 'view_arg'][0]]
        return Response(resp.iter_content(chunk_size=10*1024), ## TODO -- make a config or param
                        content_type=resp.headers['Content-Type'])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon') 
