from sandhill import app
from sandhill.utils.template import evaluate_conditions

def conditions(data_dict):
    #TODO check if conditions is a key
    condition_keys = data_dict['conditions'].split('.')

    conditions = data_dict
    for ck in condition_keys:
        if ck in conditions:
            conditions = conditions[ck]
        else:
            app.logger.warning("Invalid condition keys: {0}".format(data_dict['conditions']))
            if "on_fail" in data_dict:
                abort(data_dict["on_fail"])

    return evaluate_conditions(conditions, data_dict, match_all=False) > 0
