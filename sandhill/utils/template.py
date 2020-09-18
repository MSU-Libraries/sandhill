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
    """
    matched = 0
    for match in conditions:
        check_value = render_template(match['value'], context)
        if check_value in match['allowed']:
            # Idea: use boosts if the matched value for 2 config files is the same, e.g. matched += boost
            matched += 1
    # Only assigned matched value if ALL matches are successful
    return matched if matched == len(conditions) or not match_all else 0
