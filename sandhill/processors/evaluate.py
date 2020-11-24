'''
Processor for evaluation functions
'''
from jinja2 import TemplateError
from sandhill import app
from sandhill.utils.template import evaluate_conditions
from sandhill.utils.generic import ifnone, get_descendant_from_dict
from sandhill.utils.template import render_template

def conditions(data_dict):
    """
    Evaluates the condtions speicified in the processor section of the configs
    args:
        data_dict (dict): Dictinoary with the configs

    return:
        (bool|None): Returns True if given conditions match appropriate to the
            parameters, False if they do not, or None on failure
    """
    evaluation = None
    condition_keys = ifnone(data_dict, 'conditions', '')
    _conditions = get_descendant_from_dict(data_dict, condition_keys.split('.')
                                           if condition_keys else [])
    if 'match_all' not in data_dict or not isinstance(data_dict['match_all'], bool):
        app.logger.warning("Processor 'evaluate' is missing or has invalid 'match_all': "
                           + ifnone(data_dict, 'match_all', "not defined"))
    elif not _conditions:
        app.logger.warning("Invalid condition keys: {0}".format(
            data_dict['conditions'] if 'conditions' in data_dict else "'conditions' undefined"))
    else:
        evaluation = evaluate_conditions(_conditions,
                                         data_dict, match_all=data_dict['match_all']) > 0
        if 'abort_on_match' in data_dict and data_dict['abort_on_match'] and evaluation:
            evaluation = None

    return evaluation

def template(data_dict):
    """
    Given a Jinja2 template, it will render that template to a string and set it in the `name`
    variable.
    args:
        data_dict (dict): Dictinoary with the configs
    return:
        (string|None): rendered template to a string value
    """
    evaluation = None
    if 'value' in data_dict:
        try:
            evaluation = render_template(data_dict['value'], data_dict)
        except TemplateError as tmpl_err:
            app.logger.warning(
                f"Invalid template provided for: {data_dict['value']}. Error: {tmpl_err}")

    return evaluation
