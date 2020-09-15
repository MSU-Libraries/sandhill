from sandhill.utils import filters
from sandhill import app
from jinja2.runtime import new_context
from jinja2 import TemplateError
from pytest import raises

def test_size_format():
    assert filters.size_format(100) == "100 B"
    assert filters.size_format(2048) == "2 KB"
    assert filters.size_format(2411725) == "2.3 MB"
    assert filters.size_format(1202590843) == "1.12 GB"
    assert filters.size_format(2245202743919) == "2.04 TB"
    assert filters.size_format("big file") == "0 B"
    assert filters.size_format("5138022") == "4.9 MB"

def test_islist():
    assert filters.is_list([]) == True
    assert filters.is_list(['a',1]) == True
    assert filters.is_list({'a':1}) == False
    assert filters.is_list("string") == False
    assert filters.is_list(None) == False

def test_generate_datastream_url():
    assert filters.generate_datastream_url("etd:1000") == "/etd/1000/OBJ/view"
    assert filters.generate_datastream_url("etd/1000") == "/etd/1000/OBJ/view"
    assert filters.generate_datastream_url("etd/1000",obj_type="SOMETHING") == "/etd/1000/SOMETHING/view"
    assert filters.generate_datastream_url("etd/1000", action="forward") == "/etd/1000/OBJ/forward"
    assert filters.generate_datastream_url("else:999","OTHER","hello") == "/else/999/OTHER/hello"
    with raises(AttributeError) as aerror:
        filters.generate_datastream_url(1234)
    with raises(AttributeError) as aerror:
        filters.generate_datastream_url(None)

def test_head():
    assert filters.head([4,5,6]) == 4
    assert filters.head("string") == "string"
    assert filters.head(None) is None
    emptylist = filters.head([])
    assert isinstance(emptylist, list)
    assert not emptylist

def test_solr_escape():
    pass #TODO

def test_set_query_arg():
    pass #TODO

def test_assemble_url():
    pass #TODO

def test_date_passed():
    pass #TODO

def test_render():
    data_dict = {
        "var": "val",
        "data_name": {
            "data_var": "data_val"
        }
    }

    template = app.jinja_env.from_string("{{ var }}")
    context = template.new_context(vars=data_dict)
    assert filters.render(context, "{{ var }}") == "val"
    assert filters.render(context, "{{ data_name.data_var }}") == "data_val"

    # Testing TemplateError
    assert filters.render(context, "{{ invalid template") is None


def test_render_literal():
    data_dict = {
        "var": "val"
    }

    template = app.jinja_env.from_string("{{ var }}")
    context = template.new_context(vars=data_dict)
    # Testing literal_eval
    liter = filters.render_literal(context, "['1','2','3']")
    assert isinstance(liter, list)
    assert len(liter) == 3
    assert liter[0] == '1'

    # Testing ValueError
    liter = filters.render_literal(context, "stringwithoutspaces")
    assert liter == "stringwithoutspaces"
    with raises(ValueError) as verror:
        liter = filters.render_literal(context, "stringwithoutspaces", False)

    # Testing SyntaxError
    liter = filters.render_literal(context, "string with spaces")
    assert liter == "string with spaces"
    with raises(SyntaxError) as serror:
        liter = filters.render_literal(context, "string with spaces", False)
