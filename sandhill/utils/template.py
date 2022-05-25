'''
Template and Jinja2 utilities
'''
import json
import flask
from sandhill import filters        # pylint: disable=unused-import
from sandhill.utils import context  # pylint: disable=unused-import

def render_template_string(template_str, ctx):
    """
    Renders Jinja templates with added Sandhill filters/context processors.
    Args:
        template_str (string): jinja template variable
        ctx (dict): Context for the jinja template
    Returns:
        (str): The rendered template as a string.
    Raises:
        jinja2.TemplateError
    """
    with context.app_context():
        return flask.render_template_string(template_str, **ctx)

def evaluate_conditions(conditions, ctx, match_all=True):
    """
    Render each of the condition['value'] using the given context; the result must
    match a value in condition['allowed']
    Args:
        conditions (list): List of dict containing keys 'value' and 'allowed'
        ctx (dict): Context dictionary for template variables
        match_all (bool): If all conditions need to be matched for it to be considered
            a match. Default = True
    Returns:
        (int): returns the number of matches matched ONLY if all are matched, else returns 0
    Raises:
        KeyError: when "match_when"/"match_when_not" or "evaluate" is not in conditions
    """
    matched = 0
    for match in conditions:
        # Idea: use boosts if the matched value for 2 config files is the same,
        # e.g. matched += boost
        check_value = render_template_string(match['evaluate'], ctx)
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

def render_template_json(json_obj, ctx):
    """
    Serialize a JSON, render it as a template, then convert back to JSON
    Args:
        json_obj (dict|list): JSON represented in Python
        ctx (dict): Context for the jinja template
    Returns:
        (dict|list): The updated JSON structure
    Raises:
        json.JSONDecodeError: If the resulting templace is unable to be parsed as JSON
    """
    rendered = render_template_string(json.dumps(json_obj), ctx)
    return json.loads(rendered)
