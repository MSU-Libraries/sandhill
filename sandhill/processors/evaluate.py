'''
Processor for evaluation functions
'''
from sandhill import app
from sandhill.utils.template import evaluate_conditions
from sandhill.utils.generic import ifnone, get_descendant

def conditions(data):
    """
    Evaluates the condtions speicified in the processor section of the configs
    args:
        data (dict): Dictinoary with the configs

    return:
        (bool|None): Returns True if given conditions match appropriate to the
            parameters, False if they do not, or None on failure
    """
    evaluation = None
    condition_keys = ifnone(data, 'conditions', '')
    _conditions = get_descendant(data, condition_keys if condition_keys else [])
    if 'match_all' not in data or not isinstance(data['match_all'], bool):
        app.logger.warning("Processor 'evaluate' is missing or has invalid 'match_all': "
                           + ifnone(data, 'match_all', "not defined"))
    elif not _conditions:
        ick = data['conditions'] if 'conditions' in data else "'conditions' undefined"
        app.logger.warning(f"Invalid condition keys: {ick}")
    else:
        evaluation = evaluate_conditions(_conditions,
                                         data, match_all=data['match_all']) > 0
        if 'abort_on_match' in data and data['abort_on_match'] and evaluation:
            evaluation = None

    return evaluation
