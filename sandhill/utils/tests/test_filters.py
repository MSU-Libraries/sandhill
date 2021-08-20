import os
import re
import pytest
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

def test_head():
    assert filters.head([4,5,6]) == 4
    assert filters.head("string") == "string"
    assert filters.head(None) is None
    emptylist = filters.head([])
    assert isinstance(emptylist, list)
    assert not emptylist

def test_unescape():
    assert filters.unescape("a b &amp; c &quot; d") == 'a b & c " d'
    assert filters.unescape("&#42;") == '*'
    assert filters.unescape("&INVALIDTHING; &stuff &#invalid") == "&INVALIDTHING; &stuff &#invalid"

def test_filter_tags():
    tag_str = "a <b>tag <i class='attr'>filled</i></b> <u>string</u>"
    assert filters.filter_tags(tag_str) == "a tag filled string"
    assert filters.filter_tags(tag_str, "b") == "a <b>tag filled</b> string"
    assert filters.filter_tags(tag_str, "b", "u") == "a <b>tag filled</b> <u>string</u>"
    assert filters.filter_tags(tag_str, "i") == "a tag <i class=\"attr\">filled</i> string"
    assert filters.filter_tags("a <b>tag</b> &amp; &quot;quote&#34;") == "a tag &amp; &quot;quote&#34;"
    assert filters.filter_tags("non escaped refs \" & > <") == "non escaped refs \" & > "
    # Test some bad imputs
    assert filters.filter_tags("<a><b></a>c<d></e>") == "c"
    assert filters.filter_tags("<a <b <c d> e>", "c") == " e>"  # What did you expect?

def test_solr_encode_query():
    assert filters.solr_encode_query("a value") == r'a value'
    assert filters.solr_encode_query("a wild-card value*") == r'a wild\-card value*'
    assert filters.solr_encode_query("a wild-card value*", escape_wildcards=True) == r'a wild\-card value\*'
    assert filters.solr_encode_query("\"quoted value\"") == r'"quoted value"'
    assert filters.solr_encode_query("\"quoted wildcard*\"") == r'"quoted wildcard*"'
    assert filters.solr_encode_query("\"quote then wildcard\"*") == r'"quote then wildcard"*'
    assert filters.solr_encode_query("(boolean OR logic)") == r'(boolean OR logic)'
    assert filters.solr_encode_query("(\"quoted boolean\" OR \"logic terms\")") == r'("quoted boolean" OR "logic terms")'
    assert filters.solr_encode_query(r"(escaped boolean OR logic terms)") == r'(escaped boolean OR logic terms)'
    assert filters.solr_encode_query(r"combo phrase AND (boolean OR logic terms)") == r'combo phrase AND (boolean OR logic terms)'
    assert filters.solr_encode_query("\"combo phrase\" AND (other boolean OR \"logic terms\")") == r'"combo phrase" AND (other boolean OR "logic terms")'
    assert filters.solr_encode_query(r"[NOW-6MONTH TO NOW]") == r'[NOW-6MONTH TO NOW]'
    assert filters.solr_encode_query(r"[NOW - 6MONTH TO NOW]") == r'[NOW - 6MONTH TO NOW]'
    assert filters.solr_encode_query(r'["long ago" - 2025-05-19]') == r'["long ago" - 2025-05-19]'
    with pytest.raises(ValueError):
        filters.solr_encode_query(r"((")
    with pytest.raises(ValueError):
        filters.solr_encode_query(r"())")
    with pytest.raises(ValueError):
        filters.solr_encode_query(r"]]")

def test_solr_encode():
    # test escape
    assert filters.solr_encode("a test string") == r"a\ test\ string"
    assert filters.solr_encode("a with+") == r"a\ with\+"
    assert filters.solr_encode("a \\with+") == r"a\ \\with\+"
    assert filters.solr_encode("") == ""
    assert filters.solr_encode("hello") == "hello"
    assert filters.solr_encode("hello*?") == "hello*?"
    assert filters.solr_encode("hello* world?", escape_wildcards=True) == r'hello\*\ world\?'

    # test non-string
    assert filters.solr_encode(['test']) == ['test']
    assert filters.solr_encode(None) == None

def test_solr_decode():
    # test decode
    assert filters.solr_decode(r"a\ test\ string") == "a test string"
    assert filters.solr_decode(r"a\ with\+") == "a with+"
    assert filters.solr_decode(r"a\ \\with\+") == "a \\with+"
    assert filters.solr_decode("") == ""
    assert filters.solr_decode("hello") == "hello"
    assert filters.solr_decode("hello*?") == "hello*?"
    assert filters.solr_decode(r'hello\*\ world\?', escape_wildcards=True) == "hello* world?"

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

def test_urlquote():
    assert filters.urlquote("hello world") == 'hello%20world'
    assert filters.urlquote("a/path/to/pid:num") == 'a%2Fpath%2Fto%2Fpid%3Anum'

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

def test_sandbug_filter():
    # calling the debug logger
    filters.sandbug_filter("test")

def test_deepcopy():
    child_obj = {'z': 'z'}
    first_obj = {'a': 'b', 'c': child_obj}
    second_obj = filters.deepcopy(first_obj)
    # assert both the dict's contain same values and  do not point to the same memory location
    assert first_obj == second_obj
    assert first_obj is not second_obj
    first_obj['c']['z'] = 'NOT Z'
    # modifying the child object to verify the memeory location is not the same
    assert first_obj != second_obj

def test_getfilterquery():
    query = {
        'q': "frogs",
        'fq': ["dessert:cake", "dessert:pie", "location:East\\ Lansing", "location:St\\ John's", "colon:value:with:colons"]
    }
    # get the filter query as a dict with a list of values
    res = filters.getfilterqueries(query)
    assert res == {'dessert': ['cake', 'pie'], 'location': ["East Lansing", "St John's"], "colon": ["value:with:colons"]}

    query = {
        'q': "frogs",
        'fq': "dessert:custard"
    }
    # get the filter query as a dict with a list of values
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

    # adding field and value to the filter query
    res = filters.addfilterquery(query, 'dessert', "pie")
    assert res == {'q': "frogs", 'fq': ["dessert:cake", "dessert:pie"]}

    # test with a 'start' param to make sure it is removed
    query['start'] = 20
    res = filters.addfilterquery(query, 'test', 'coolthing')
    assert res == {'q': "frogs", 'fq': ["dessert:cake", "dessert:pie", "test:coolthing"]}

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
    # Pass a non existing field and value to compare with the filter query
    res = filters.hasfilterquery(query, 'dessert', "ice cream")
    assert res == False

    query = {
        'q': "frogs",
        'fq': "dessert:cake"
    }

    # Pass a non existing field and value to compare with the filter query
    res = filters.hasfilterquery(query, 'dessert', "ice cream")
    assert res == False

    # Pass an existing field and value to compare with the filter query
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

    # test with a 'start' param to make sure it is removed
    query['start'] = 20
    res = filters.removefilterquery(query, 'test', 'coolthing')
    assert res == {'q': "frogs", 'fq': []}

    # TEMP test for fix_preescaped_query
    query = {
        'q': "frogs",
        'fq': ["dessert:(cake OR \"ice cream\")"]
    }
    res = filters.removefilterquery(query, 'dessert', '(cake OR \"ice cream\")')
    assert res == {'q': "frogs", 'fq': []}

def test_maketuplelist():
    example_list = ['xyz', 1, 'abc', 3]
    # test with a list with evenly divisible tuple count
    res = filters.maketuplelist(example_list, 2)
    assert [('xyz', 1), ('abc', 3)] == res

    # test with a list with evenly divisible tuple count
    example_list = ['xyz', 1, 2, 'abc', 3, 4]
    res = filters.maketuplelist(example_list, 3)
    assert [('xyz', 1, 2), ('abc', 3, 4)] == res

    # test with a list with unevenly divisible tuple count
    example_list = ['xyz', 1, 2, 'abc', 3, 4]
    res = filters.maketuplelist(example_list, 4)
    assert [('xyz', 1, 2, 'abc')] == res

def test_makedict():
    example_list = ['xyz', 1, 'abc', 3]
    # test with a list with evenly divisible count
    res = filters.makedict(example_list)
    assert {'xyz':1, 'abc': 3} == res

    # test with a list with unevenly divisible count
    example_list = ['xyz', 1, 2, 'abc', 3]
    res = filters.makedict(example_list)
    assert {'xyz': 1, 2:'abc'} == res

def test_regex_match():
    # perform a positive match
    value = "StillImage"
    pattern = r"^Still"
    res = filters.regex_match(value, pattern)
    assert res is not None
    assert res
    assert res.group() == "Still"

    # unable to match
    value = "Movie"
    res = filters.regex_match(value, pattern)
    assert res is None

    # passing an invalid regex patterns
    value = "StillImage"
    pattern = r"(??!^.)([A-Z])"
    res = filters.regex_match(value, pattern)
    assert res is None

def test_regex_sub():
    value = "StillImage"
    pattern = r"(?!^.)([A-Z])"
    substitute = r" \1"
    res = filters.regex_sub(value, pattern, substitute)
    assert "Still Image" == res

    # test by passing a list instead of a string
    value = ["StillImage"]
    res = filters.regex_sub(value, pattern, substitute)
    assert value == res

    # test by passing an invalid regex
    value = "StillImage"
    pattern = r"(??!^.)([A-Z])"
    res = filters.regex_sub(value, pattern, substitute)
    assert value == res
