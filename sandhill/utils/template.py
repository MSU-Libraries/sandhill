from jinja2 import Environment
from inspect import getmembers, isfunction
from sandhill.utils import filters

def render_template(template_str, context):
    """
    Renders jinja templates
    args:
        template_str (string): jinja template variable
        context (dict): Context for the jinja template
    raises:
        jinja2.TemplateError
    """
    env = Environment()
    sandhill_filters = dict([f for f in getmembers(filters) if isfunction(f[1])])
    env.filters = {**env.filters, **sandhill_filters}
    data_template = env.from_string(template_str)
    return data_template.render(**context)

def evaluate_conditions(conditions, context, match_all=True):
    """
    Render each of the condition['value'] using the given context; the result must 
    match a value in condition['allowed']
    args:
        conditions (list): List of dict containing keys 'value' and 'allowed'
        context (dict): Context dictionary for template variables
        match_all (bool): If all conditions need to be matched for it to be considered 
            a match. Default = True
    return:
        (int): returns the number of matches matched ONLY if all are matched, else returns 0
    raises
        KeyError: when "match_when"/"match_when_not" or "evaluate" is not in conditions
    """
    matched = 0
    for match in conditions:
        # Idea: use boosts if the matched value for 2 config files is the same, e.g. matched += boost
        check_value = render_template(match['evaluate'], context)
        if not any(key in ['match_when', 'match_when_not'] for key in match.keys()) or \
            {'match_when', 'match_when_not'}.issubset(set(match.keys())):
            raise KeyError("One (and only one) of the keys 'match_when' or 'match_when_not' must be present")
        elif 'match_when' in match and check_value in match['match_when']:
            matched += 1
        elif 'match_when_not' in match and check_value not in match['match_when_not']:
            matched += 1
    # Only assigned matched value if ALL matches are successful
    return matched if matched == len(conditions) or not match_all else 0
