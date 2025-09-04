'''
Processor for evaluation functions
'''
from sandhill import app
from sandhill.utils.template import evaluate_conditions
from sandhill.utils.generic import ifnone, getdescendant
from sandhill.utils.error_handling import dp_abort

def conditions(data):
    """
    Evaluates the conditions specified in the processor section of the configs.\n
    [Detailed documentation](https://msu-libraries.github.io/sandhill/evaluate-conditions/) \n
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `conditions` _string_: Indicates the location in `data` where conditions to be \
                evaluated are.\n
                This is a `.` delimited string of dict keys and/or list indexes.\n
            * `match_all` _boolean__: Whether to require all conditions to match for success; \
                if false, any single match will be considered a success.\n
            * `abort_on_match` _boolean, optional_: If true, then trigger an abort when the \
                conditions are truthy.\n
    Returns:
        (bool|None): Returns True if given conditions match appropriate to the \
                     parameters, False if they do not, or None on failure
    Raises:
        HTTPException: If `abort_on_match` is true and the evaluation is truthy.
    """
    # TODO refactor suggestion:
    #   replace `match_all` with `match` key; new possible values:
    #       "all"  : similar to match_all: True
    #       "any"  : similar to match_all: False
    #       "none" : new state which considers success when 0 matches
    evaluation = None
    condition_keys = ifnone(data, 'conditions', '')
    _conditions = getdescendant(data, condition_keys if condition_keys else [])
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
            dp_abort(503)
            evaluation = None

    return evaluation
