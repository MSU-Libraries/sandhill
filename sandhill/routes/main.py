import os
import collections
from flask import Flask, request, render_template, url_for, send_from_directory
from .. import app
from ..utils.decorators import add_routes
from ..utils.config_loader import load_route_config
from ..processors.base import load_data


@add_routes()
def main(*args, **kwargs):
    route_used = request.url_rule.rule
    ## loop over all the configs in the instance dir looking at the "route"
    ## field to determine which configs to use
    route_config = load_route_config(route_used)

    ## loop over 'data' to gather data for the template
    data = {}
    if 'data' in route_config and 'name':
        for d in [d for d in route_config['data'] if 'name' in d]:
            data[d['name']] = load_data(d, data)

    ## render the tempate with the data
    return render_template(route_config['template'], **data)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon') 
