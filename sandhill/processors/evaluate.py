from sandhill import app
from sandhill.utils.template import evaluate_conditions
from sandhill.utils.generic import ifnone, get_descendant_from_dict
from flask import abort

def conditions(data_dict):
    """
    Evaluates the condtions speicified in the processor section of the configs
    args:
        data_dict (dict): Dictinoary with the configs

    return:
        (bool|None): Returns True if given conditions match appropriate to the parameters, False if they do not, or None on failure
    """
    evaluation = None
    condition_keys = ifnone(data_dict,'conditions', '')
    conditions = get_descendant_from_dict(data_dict, condition_keys.split('.') if condition_keys else [])

    if 'match_all' not in data_dict or not isinstance(data_dict['match_all'], bool):
        app.logger.warning("Processor 'evaluate' is missing or has invalid 'match_all': "
                           + ifnone(data_dict, 'match_all', "not defined"))
    elif not conditions:
        app.logger.warning("Invalid condition keys: {0}".format(
            data_dict['conditions'] if 'conditions' in data_dict else "'conditions' undefined"))
    else:
        evaluation = evaluate_conditions(conditions, data_dict, match_all=data_dict['match_all']) > 0

    return evaluation
