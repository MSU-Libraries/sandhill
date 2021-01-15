from pytest import raises
from sandhill.utils import template
from jinja2 import TemplateError


def test_render_template():
    # Test if the template variables are rendered as expected
    context = {
        "var1": "val1",
        "var2": "val2",
        "date": "3029-01-01"
    }
    assert template.render_template("{{ var1 }}", context) == "val1"
    assert template.render_template("{{ var3 }}", context) == ""
    assert template.render_template("{{ date | date_passed }}", context) == "False"

    # Test raising a template error 
    with raises(TemplateError):
        template.render_template("{{ var1 }", context)

def test_evaluate_conditions():
    conditions = [
        {
            "evaluate": "{{ item.embargo_end_date_ss | head | date_passed if item.embargo_end_date_ss is defined else True }}",
            "match_when": ["False"]
        },
        {
            "evaluate": "{{ 'embargoed' if item.embargo_datastream_ss is not defined or datastream_label in item.embargo_datastream_ss else 'accessible' }}",
            "match_when": ["embargoed"]
        }
    ]
    context = {
        "item": {
            "embargo_end_date_ss":["3029-01-01"],
            "embargo_datastream_ss":["OBJ", "FULL_TEXT"]
            },
        "datastream_label": "OBJ"
    }
    assert template.evaluate_conditions(conditions, context, match_all=True) == 2
    
    # change the datastream_label to an allowed datastream
    context["datastream_label"] = "TN"
    assert template.evaluate_conditions(conditions, context, match_all=True) == 0
    assert template.evaluate_conditions(conditions, context, match_all=False) == 1

    # invalid keys in conditions
    conditions = [
        {
            "value": "{{ Value is not an allowed key }}",
            "allowed": ["False"]
        },
        {
            "value": "{{ Value is not an allowed key }}",
            "allowed": ["embargoed"]
        }
    ]
    with raises(KeyError):
        template.evaluate_conditions(conditions, context, match_all=True)
   
    # when conditions are empty
    conditions =[]
    assert template.evaluate_conditions(conditions, context, match_all=True) == 0
    
    # when all the conditions dont match
    conditions = [
        {
            "evaluate": "{{ item.embargo_end_date_ss | head | date_passed if item.embargo_end_date_ss is defined else True }}",
            "match_when": ["True"]
        },
        {
            "evaluate": "{{ 'embargoed' if item.embargo_datastream_ss is not defined or datastream_label in item.embargo_datastream_ss else 'accessible' }}",
            "match_when": ["embargoed"]
        }
    ]
    assert template.evaluate_conditions(conditions, context, match_all=True) == 0

    # use of match_when_not
    conditions = [
        {
            "evaluate": "{{ datastream_label }}",
            "match_when_not": ["TN"]
        }
    ]
    assert template.evaluate_conditions(conditions, context, match_all=True) == 0
    conditions[0]['match_when_not'] = ['OBJ']
    assert template.evaluate_conditions(conditions, context, match_all=True) == 1

    # attempted use of both match_when and match_when_not
    conditions = [
        {
            "evaluate": "{{ datastream_label }}",
            "match_when_not": ["TN"],
            "match_when": ["OBJ"]
        }
    ]
    with raises(KeyError):
        template.evaluate_conditions(conditions, context, match_all=True)

