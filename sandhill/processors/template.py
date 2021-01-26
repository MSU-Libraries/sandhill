'''
Processor for rendering templates
'''
from flask import render_template, abort, make_response
from jinja2.exceptions import TemplateNotFound, TemplateError
from sandhill import app

def render(data_dict):
    '''
    Render the response as a template or directly as a Flask Response
    args:
        data_dict (dict): The route_config 'data' section
    returns:
        Renders the response via a template or provided Flask Response
    '''
    try:
        if 'file' not in data_dict:
            app.logger.error("template var: 'file' not set in config. Unable to render response.")
            abort(500)
        template = data_dict["file"]

        return make_response(render_template(template, **data_dict))
    except TemplateNotFound as tmpl_exe:
        app.logger.warning(f"Failure when rendering {template}."
                           f"Could not find template to render: {tmpl_exe}")
        abort(501)
    except TemplateError as tmpl_exe:
        app.logger.warning(f"An error has occured when rendering {template}: {tmpl_exe}")
        abort(500)
