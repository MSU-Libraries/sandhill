import os
from sandhill.utils import filters
from sandhill import app
from jinja2.runtime import new_context
from jinja2 import TemplateError
from pytest import raises

def test_size_format():
    assert filters.size_format(100) == "100 B"
    assert filters.size_format(2048) == "2 KB"
    assert filters.size_format(2411725) == "2.3 MB"
    assert filters.size_format(1202590843) == "1.1 GB"
    assert filters.size_format(2245202743919) == "2 TB"
    assert filters.size_format("big file") == "0 B"
    assert filters.size_format("5138022") == "4.9 MB"

def test_get_extension():
    assert filters.get_extension('application/pdf') == "PDF"
    assert filters.get_extension('image/jpeg') == "JPG"
    assert filters.get_extension('image/png') == "PNG"
    assert filters.get_extension('text/plain') == "TXT"
    assert filters.get_extension('undefined/undefined') == "???"

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
    # test escape
    assert filters.solr_escape("a test string") == r"a\ test\ string"
    assert filters.solr_escape("a with+") == r"a\ with\+"
    assert filters.solr_escape("a \\with+") == r"a\ \\with\+"
    assert filters.solr_escape("") == ""
    assert filters.solr_escape("hello") == "hello"

    # test non-string
    assert filters.solr_escape(['test']) == ['test']
    assert filters.solr_escape(None) == None

def test_solr_decode():
    # test decode
    assert filters.solr_decode(r"a\ test\ string") == "a test string"
    assert filters.solr_decode(r"a\ with\+") == "a with+"
    assert filters.solr_decode(r"a\ \\with\+") == "a \\with+"
    assert filters.solr_decode("") == ""
    assert filters.solr_decode("hello") == "hello"

    # test non-string
    assert filters.solr_decode(['test']) == ['test']
    assert filters.solr_decode(None) == None

def test_set_child_key():
    args = {}

    # test adding when key isn't already there
    assert filters.set_child_key(args, 'query_args', 'a', 'b') == {"query_args": {"a": "b"}}

    # test adding to an existing arg list
    assert filters.set_child_key(args, 'query_args', 'c', 'd') == {"query_args": {"a": "b", "c": "d"}}

    # test overwriting a key
    assert filters.set_child_key(args, 'query_args', 'a', 'b2') == {"query_args": {"a": "b2", "c": "d"}}

    # test providing a non-string key
    assert filters.set_child_key(args, 'query_args', 1, 2) == {"query_args": {"a": "b2", "c": "d", 1: 2}}

    # test providing a list as a key
    assert filters.set_child_key(args, 'query_args', [1], 2) == {"query_args":{"a": "b2", "c": "d", 1: 2}}

    # test providing a non-dict
    args2 = ['test']
    assert filters.set_child_key(args2, 'query_args', 1, 2) == ['test']

def test_assemble_url():
    url_components = {
        "path": "https://mytest.com",
    }
    # Test positive scenarios
    assert filters.assemble_url(url_components) == "https://mytest.com"

    url_components["query_args"] = {}
    assert filters.assemble_url(url_components) == "https://mytest.com"

    url_components["query_args"] = {"q":"'hi'"}
    assert filters.assemble_url(url_components) == "https://mytest.com?q=%27hi%27"

    url_components["query_args"]["another"] = "value with space"
    assert filters.assemble_url(url_components) == "https://mytest.com?q=%27hi%27&another=value+with+space"

    # test missing path
    del url_components["path"]
    assert filters.assemble_url(url_components) == ""

    # test non-dict query_args
    url_components["path"] = "mysite"
    url_components["query_args"] = 1
    assert filters.assemble_url(url_components) == "mysite"

    # test non-dict url_components
    assert filters.assemble_url("hello") == ""

def test_date_passed():
    # Test positive scenarios
    assert filters.date_passed('2000-01-01') == True
    assert filters.date_passed('2040-01-01') == False

    # Test bad input
    assert filters.date_passed('not-a-date') == False
    assert filters.date_passed(2000) == False

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

def test_format_date():
    # Test with valid end date
    res = filters.format_date("2020-12-31")
    assert res == "December 31st, 2020"
    res = filters.format_date("2022-01-03")
    assert res == "January 3rd, 2022"
    res = filters.format_date("8000-01-03")
    assert res == "January 3rd, 8000"

    # Test with indenfinite end date
    res = filters.format_date("9999-12-31")
    assert res == "Indefinite"
    res = filters.format_date("")
    assert res == "Indefinite"
    res = filters.format_date(None)
    assert res == "Indefinite"

    # Test with wrong datatype passed
    res = filters.format_date(123)
    assert res == "Indefinite"

    # Test wrong format passed
    res = filters.format_date("abc")
    assert res == "Indefinite"
    res = filters.format_date("01-01-2020")
    assert res == "Indefinite"

    # Test overriding the default value
    res = filters.format_date("9999-12-31", "different")
    assert res == "different"

def test_sandbug():
    # calling the debug logger
    filters.sandbug("test") 

def test_deepcopy():
    child_obj = {'z': 'z'}
    first_obj = {'a': 'b', 'c': child_obj}
    second_obj = filters.deepcopy(first_obj)
    assert first_obj == second_obj
    assert first_obj is not second_obj
    first_obj['c']['z'] = 'NOT Z'
    assert first_obj != second_obj

def test_getfilterquery():
    query = {
        'q': "frogs",
        'fq': ["dessert:cake", "dessert:pie", "location:East\\ Lansing", "location:St\\ John's", "colon:value:with:colons"]
    }
    res = filters.getfilterqueries(query)
    assert res == {'dessert': ['cake', 'pie'], 'location': ["East Lansing", "St John's"], "colon": ["value:with:colons"]}

    query = {
        'q': "frogs",
        'fq': "dessert:custard"
    }
    res = filters.getfilterqueries(query)
    assert res == {'dessert': ['custard']}

def test_addfilterquery():
    query = {
        'q': "frogs"
    }
    res = filters.addfilterquery(query, 'location', "East Lansing")
    assert res == {'q': "frogs", 'fq': ["location:East\\ Lansing"]}

    # adding multiple times only results in a single entry
    res = filters.addfilterquery(res, 'location', "East Lansing")
    assert res == {'q': "frogs", 'fq': ["location:East\\ Lansing"]}

    query = {
        'q': "frogs",
        'fq': "dessert:cake"
    }
    res = filters.addfilterquery(query, 'dessert', "pie")
    assert res == {'q': "frogs", 'fq': ["dessert:cake", "dessert:pie"]}

def test_hasfilterquery():
    query = {
        'q': "frogs",
        'fq': ["dessert:cake", "location:East\\ Lansing"]
    }
    res = filters.hasfilterquery(query, 'location', "East Lansing")
    assert res == True

    query = {
        'q': "frogs",
        'fq': ["dessert:cake", "location:East\\ Lansing"]
    }
    res = filters.hasfilterquery(query, 'dessert', "ice cream")
    assert res == False

    query = {
        'q': "frogs",
        'fq': "dessert:cake"
    }
    res = filters.hasfilterquery(query, 'dessert', "ice cream")
    assert res == False
    res = filters.hasfilterquery(query, 'dessert', "cake")
    assert res == True

def test_removefilterquery():
    query = {
        'q': "frogs",
        'fq': ["dessert:cake", "location:East\\ Lansing"]
    }
    res = filters.removefilterquery(query, 'location', "East Lansing")
    assert res == {'q': "frogs", 'fq': ["dessert:cake"]}

    # removing a filterquery that doesn't exist doesn't do anything
    res = filters.removefilterquery(query, 'notafield', "Not a value")
    assert res == {'q': "frogs", 'fq': ["dessert:cake"]}

    query = {
        'q': "frogs",
        'fq': "dessert:cake"
    }
    res = filters.removefilterquery(query, 'dessert', "cake")
    assert res == {'q': "frogs", 'fq': []}
