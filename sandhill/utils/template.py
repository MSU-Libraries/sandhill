'''
Template and Jinja2 utilities
'''
import json
import flask
from sandhill.utils import filters, context     # pylint: disable=unused-import

def render_template_string(template_str, context):
    """
    Renders jinja templates
    args:
        template_str (string): jinja template variable
        context (dict): Context for the jinja template
    raises:
        jinja2.TemplateError
    """
    return flask.render_template_string(template_str, **context)

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
        # Idea: use boosts if the matched value for 2 config files is the same,
        # e.g. matched += boost
        check_value = render_template_string(match['evaluate'], context)
        if not any(key in ['match_when', 'match_when_not'] for key in match.keys()) or \
            {'match_when', 'match_when_not'}.issubset(set(match.keys())):
            raise KeyError(
                "One (and only one) of the keys 'match_when' or 'match_when_not' must be present"
            )
        if 'match_when' in match and check_value in match['match_when']:
            matched += 1
        elif 'match_when_not' in match and check_value not in match['match_when_not']:
            matched += 1
    # Only assigned matched value if ALL matches are successful
    return matched if matched == len(conditions) or not match_all else 0

def render_template_json(json_obj, context):
    """
    Serialize a JSON, render it as a template, then convert back to JSON
    args:
        json_obj(dict|list): JSON represented in Python
        context (dict): Context for the jinja template
    returns:
        (dict|list): The updated JSON structure
    throws:
        json.JSONDecodeError: If the resulting templace is unable to be
        parsed as JSON
    """
    rendered = render_template_string(json.dumps(json_obj), context)
    return json.loads(rendered)
