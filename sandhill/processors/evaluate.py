'''
Processor for evaluation functions
'''
from sandhill import app
from sandhill.utils.template import evaluate_conditions
from sandhill.utils.generic import ifnone, get_descendant

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
    _conditions = get_descendant(data_dict, condition_keys if condition_keys else [])
    if 'match_all' not in data_dict or not isinstance(data_dict['match_all'], bool):
        app.logger.warning("Processor 'evaluate' is missing or has invalid 'match_all': "
                           + ifnone(data_dict, 'match_all', "not defined"))
    elif not _conditions:
        ick = data_dict['conditions'] if 'conditions' in data_dict else "'conditions' undefined"
        app.logger.warning(f"Invalid condition keys: {ick}")
    else:
        evaluation = evaluate_conditions(_conditions,
                                         data_dict, match_all=data_dict['match_all']) > 0
        if 'abort_on_match' in data_dict and data_dict['abort_on_match'] and evaluation:
            evaluation = None

    return evaluation
