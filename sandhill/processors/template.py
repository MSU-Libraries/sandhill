'''
Processor for rendering templates
'''
from flask import render_template, abort, make_response
from jinja2.exceptions import TemplateNotFound, TemplateError
from sandhill import app, catch
from sandhill.utils.template import render_template_string

@catch(TemplateError, "An error has occured when rendering {data_dict[file]}: {exc}", abort=500)
@catch(TemplateNotFound, "Failure when rendering {data_dict[file]}. " \
       "Could not find template to render: {exc}", abort=501)
def render(data_dict):
    '''
    Render the response as a template or directly as a Flask Response
    args:
        data_dict (dict): The route_config 'data' section
    returns:
        Renders the response via a template or provided Flask Response
    '''
    if 'file' not in data_dict:
        app.logger.error("template var: 'file' not set in config. Unable to render response.")
        abort(500)
    template = data_dict["file"]

    return make_response(render_template(template, **data_dict))

@catch(TemplateError, "Invalid template provided for: {data_dict[value]}. Error: {exc}",
       return_val=None)
def render_string(data_dict):
    """
    Given a Jinja2 template string, it will render that template to a string and set it in
    the `name` variable.
    args:
        data_dict (dict): Dictinoary with the configs
    return:
        (string|None): rendered template to a string value
    """
    evaluation = None
    if 'value' in data_dict:
        evaluation = render_template_string(data_dict['value'], data_dict)
    return evaluation
