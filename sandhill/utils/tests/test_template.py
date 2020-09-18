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


