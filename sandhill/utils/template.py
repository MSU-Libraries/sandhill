'''
Template and Jinja2 utilities
'''
import json
import flask
from sandhill import filters        # pylint: disable=unused-import
from sandhill.utils import context  # pylint: disable=unused-import

def render_template_string(template_str, ctx):
    """
    Renders Jinja templates with added Sandhill filters/context processors. \n
    Args:
        template_str (string): jinja template variable \n
        ctx (dict): Context for the jinja template \n
    Returns:
        (str): The rendered template as a string. \n
    Raises:
        jinja2.TemplateError: On invalid template. \n
    """
    with context.app_context():
        return flask.render_template_string(template_str, **ctx)

def evaluate_conditions(conditions, ctx, match_all=True):
    """
    Render each conditions' `evaluate` using the given context; the result must \
    match a value in the conditions' `match_when` or none of the conditions' `match_when_not`. \n
    Args:
        conditions (list): List of dict containing keys 'value' and 'allowed' \n
        ctx (dict): Context dictionary for template variables \n
        match_all (bool): If all conditions need to be matched for it to be considered \
            a match. \n
            Default: True \n
    Returns:
        (int): returns the number of matches matched ONLY if all are matched, else returns 0 \n
    Raises:
        KeyError: when "match_when"/"match_when_not" or "evaluate" is not in conditions \n
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
    Serialize a JSON, render it as a template, then convert back to JSON \n
    Args:
        json_obj (dict|list): JSON represented in Python \n
        ctx (dict): Context for the jinja template \n
    Returns:
        (dict|list): The updated JSON structure \n
    Raises:
        json.JSONDecodeError: If the resulting templace is unable to be parsed as JSON \n
    """
    # Disable autoescape for JSON output to avoid HTML entities being injected
    rendered = render_template_string(
        "{% autoescape false -%}" +
        json.dumps(json_obj) +
        "{%- endautoescape %}",
        ctx
    )
    return json.loads(rendered)
