'''
Processor for rendering templates
'''
from flask import render_template, abort, make_response
from jinja2.exceptions import TemplateNotFound, TemplateError
from sandhill import app, catch
from sandhill.utils.template import render_template_string

@catch(TemplateError, "An error has occured when rendering {data[file]}: {exc}", abort=500)
@catch(TemplateNotFound, "Failure when rendering {data[file]}. " \
       "Could not find template to render: {exc}", abort=501)
def render(data):
    '''
    Render the response as a template or directly as a Flask Response.
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `file` _str_: Path to the template file.\n
    Returns:
        (flask.Response): The rendered template in a Flask response.
    Raises:
        wergzeug.exceptions.HTTPException: If `file` is not set in data.
    '''
    if 'file' not in data:
        app.logger.error("template.render: 'file' not set in data; unable to render response.")
        abort(500)
    template = data["file"]

    return make_response(render_template(template, **data))

@catch(TemplateError, "Invalid template provided for: {data[value]}. Error: {exc}",
       return_val=None)
def render_string(data):
    """
    Given a Jinja2 template string, it will render that template to a string and set it in
    the `name` variable.
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `value` _str_: The template string to render.\n
    Returns:
        (str|None): The rendered template string, or None if no `value` key was in data.
    """
    evaluation = None
    if 'value' in data:
        evaluation = render_template_string(data['value'], data)
    return evaluation
