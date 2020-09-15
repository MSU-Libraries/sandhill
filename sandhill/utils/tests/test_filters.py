from sandhill.utils import filters
from sandhill import app
from jinja2.runtime import new_context

def test_islist():
    assert filters.is_list([]) == True
    assert filters.is_list(['a',1]) == True
    assert filters.is_list({'a':1}) == False
    assert filters.is_list("string") == False
    assert filters.is_list(None) == False

def test_render():

    data_dict = {
        "var": "val"
    }

    template = app.jinja_env.from_string("{{ var }}")
    context = template.new_context(vars=data_dict)
    assert filters.render(context, "{{ var }}") == "val"

