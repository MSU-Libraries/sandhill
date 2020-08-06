from sandhill import app
from sandhill.utils.template import evaluate_conditions
from sandhill.utils.generic import ifnone, get_descendant_from_dict
from flask import abort

def conditions(data_dict):
    condition_keys = ifnone(data_dict,'conditions', '')
    conditions = get_descendant_from_dict(data_dict, condition_keys.split('.') if condition_keys else [])

    if not conditions:
        app.logger.warning("Invalid condition keys: {0}".format(data_dict['conditions']))
        if "on_fail" in data_dict:
            abort(data_dict["on_fail"])

    return evaluate_conditions(conditions, data_dict, match_all=False) > 0
