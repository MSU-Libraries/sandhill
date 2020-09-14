from sandhill.utils import filters
from sandhill import app

def test_islist():
    assert filters.is_list([]) == True
    assert filters.is_list(['a',1]) == True
    assert filters.is_list({'a':1}) == False
    assert filters.is_list("string") == False
    assert filters.is_list(None) == False

def test_render():

    data_dict = {
        "environment": {
            "var": "val"
        }
    }

    # Test rendering a value from the context
    with app.test_request_context('/etd/1000'):
        #ctx = app.app_context()
        print(app.__dict__)
        print(app.template_context_processors.__dict__)
        print(type(app.jinja_env.render(data_dict)))
        print(app.jinja_env.render(data_dict))
        assert filters.render("just no", "{{ var }}") == "val"
