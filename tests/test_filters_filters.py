import os
import re
import pytest
from sandhill import app
from sandhill import filters
from sandhill.utils import generic
from jinja2.runtime import new_context
from jinja2 import TemplateError
from pytest import raises

def test_filter_formatbinary():
    assert filters.formatbinary(100) == "100 B"
    assert filters.formatbinary(2048) == "2 KB"
    assert filters.formatbinary(2411725) == "2.3 MB"
    assert filters.formatbinary(1202590843) == "1.1 GB"
    assert filters.formatbinary(2245202743919) == "2 TB"
    assert filters.formatbinary("big file") == "0 B"
    assert filters.formatbinary("5138022") == "4.9 MB"

def test_filter_getextension():
    assert filters.getextension('application/pdf') == "PDF"
    assert filters.getextension('image/jpeg') == "JPG"
    assert filters.getextension('image/png') == "PNG"
    assert filters.getextension('text/plain') == "TXT"
    assert filters.getextension('undefined/undefined') == "???"

def test_filter_islist():
    assert filters.islist([]) == True
    assert filters.islist(['a',1]) == True
    assert filters.islist({'a':1}) == False
    assert filters.islist("string") == False
    assert filters.islist(None) == False

def test_filter_head():
    assert filters.head([4,5,6]) == 4
    assert filters.head("string") == "string"
    assert filters.head(None) is None
    emptylist = filters.head([])
    assert isinstance(emptylist, list)
    assert not emptylist

def test_filter_unescape():
    assert filters.unescape("a b &amp; c &quot; d") == 'a b & c " d'
    assert filters.unescape("&#42;") == '*'
    assert filters.unescape("&INVALIDTHING; &stuff &#invalid") == "&INVALIDTHING; &stuff &#invalid"

def test_filter_filtertags():
    tag_str = "a <b>tag <i class='attr'>filled</i></b> <u>string</u>"
    assert filters.filtertags(tag_str) == "a tag filled string"
    assert filters.filtertags(tag_str, "b") == "a <b>tag filled</b> string"
    assert filters.filtertags(tag_str, "b", "u") == "a <b>tag filled</b> <u>string</u>"
    assert filters.filtertags(tag_str, "i") == "a tag <i class=\"attr\">filled</i> string"
    assert filters.filtertags("a <b>tag</b> &amp; &quot;quote&#34;") == "a tag &amp; &quot;quote&#34;"
    assert filters.filtertags("non escaped refs \" & > <") == "non escaped refs \" & > "
    # Handle use of & without a trailing ; (we escape the amp and leave the name as is
    assert filters.filtertags("unintended ref: AT&T does phones") == "unintended ref: AT&amp;T does phones"
    # Test some bad imputs
    assert filters.filtertags("<a><b></a>c<d></e>") == "c"
    assert filters.filtertags("<a <b <c d> e>", "c") == " e>"  # What did you expect?

def test_filter_solr_encodequery():
    assert filters.solr_encodequery("a value") == r'a value'
    assert filters.solr_encodequery("a wild-card value*") == r'a wild\-card value*'
    assert filters.solr_encodequery("a wild-card value*", escape_wildcards=True) == r'a wild\-card value\*'
    assert filters.solr_encodequery("\"quoted value\"") == r'"quoted value"'
    assert filters.solr_encodequery("\"quoted wildcard*\"") == r'"quoted wildcard*"'
    assert filters.solr_encodequery("\"quote then wildcard\"*") == r'"quote then wildcard"*'
    assert filters.solr_encodequery("(boolean OR logic)") == r'(boolean OR logic)'
    assert filters.solr_encodequery("(\"quoted boolean\" OR \"logic terms\")") == r'("quoted boolean" OR "logic terms")'
    assert filters.solr_encodequery(r"(escaped boolean OR logic terms)") == r'(escaped boolean OR logic terms)'
    assert filters.solr_encodequery(r"combo phrase AND (boolean OR logic terms)") == r'combo phrase AND (boolean OR logic terms)'
    assert filters.solr_encodequery("\"combo phrase\" AND (other boolean OR \"logic terms\")") == r'"combo phrase" AND (other boolean OR "logic terms")'
    assert filters.solr_encodequery(r"[NOW-6MONTH TO NOW]") == r'[NOW-6MONTH TO NOW]'
    assert filters.solr_encodequery(r"[NOW - 6MONTH TO NOW]") == r'[NOW - 6MONTH TO NOW]'
    assert filters.solr_encodequery(r'["long ago" - 2025-05-19]') == r'["long ago" - 2025-05-19]'
    with pytest.raises(ValueError):
        filters.solr_encodequery(r"((")
    with pytest.raises(ValueError):
        filters.solr_encodequery(r"())")
    with pytest.raises(ValueError):
        filters.solr_encodequery(r"]]")

def test_filter_solr_encode():
    # test escape
    assert filters.solr_encode("a test string") == r"a\ test\ string"
    assert filters.solr_encode("a with+") == r"a\ with\+"
    assert filters.solr_encode("a \\with+") == r"a\ \\with\+"
    assert filters.solr_encode("") == ""
    assert filters.solr_encode("hello") == "hello"
    assert filters.solr_encode("hello*?") == "hello*?"
    assert filters.solr_encode("hello* world?", escape_wildcards=True) == r'hello\*\ world\?'
    assert filters.solr_encode("\"hello\\world\"", preserve_quotes=True) == r'"hello\\world"'
    assert filters.solr_encode("\"hello\\world\"") == r'\"hello\\world\"'

    # test non-string
    assert filters.solr_encode(['test']) == ['test']
    assert filters.solr_encode(None) == None

def test_filter_solr_decode():
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

def test_filter_setchildkey():
    args = {}

    # test adding when key isn't already there
    assert filters.setchildkey(args, 'query_args', 'a', 'b') == {"query_args": {"a": "b"}}

    # test adding to an existing arg list
    assert filters.setchildkey(args, 'query_args', 'c', 'd') == {"query_args": {"a": "b", "c": "d"}}

    # test overwriting a key
    assert filters.setchildkey(args, 'query_args', 'a', 'b2') == {"query_args": {"a": "b2", "c": "d"}}

    # test providing a non-string key
    assert filters.setchildkey(args, 'query_args', 1, 2) == {"query_args": {"a": "b2", "c": "d", 1: 2}}

    # test providing a list as a key
    assert filters.setchildkey(args, 'query_args', [1], 2) == {"query_args":{"a": "b2", "c": "d", 1: 2}}

    # test providing a non-dict
    args2 = ['test']
    assert filters.setchildkey(args2, 'query_args', 1, 2) == ['test']

def test_filter_assembleurl():
    urlcomponents = {
        "path": "https://mytest.com",
    }
    # Test positive scenarios
    assert filters.assembleurl(urlcomponents) == "https://mytest.com"

    urlcomponents["query_args"] = {}
    assert filters.assembleurl(urlcomponents) == "https://mytest.com"

    urlcomponents["query_args"] = {"q":"'hi'"}
    assert filters.assembleurl(urlcomponents) == "https://mytest.com?q=%27hi%27"

    urlcomponents["query_args"]["another"] = "value with space"
    assert filters.assembleurl(urlcomponents) == "https://mytest.com?q=%27hi%27&another=value+with+space"

    # test missing path
    del urlcomponents["path"]
    assert filters.assembleurl(urlcomponents) == ""

    # test non-dict query_args
    urlcomponents["path"] = "mysite"
    urlcomponents["query_args"] = 1
    assert filters.assembleurl(urlcomponents) == "mysite"

    # test non-dict urlcomponents
    assert filters.assembleurl("hello") == ""

    # Removal of 'hidden' arguments
    urlcomponents = {
        "path": "https://mytest.com",
        "query_args": {
            'target': 'rama',
            '_min_year': 2001,
            '_max_year': 2010
        }
    }
    assert filters.assembleurl(urlcomponents) == "https://mytest.com?target=rama"

def test_filter_urlquote():
    assert filters.urlquote("hello world") == 'hello%20world'
    assert filters.urlquote("a/path/to/pid:num") == 'a%2Fpath%2Fto%2Fpid%3Anum'

def test_filter_datepassed():
    # Test positive scenarios
    assert filters.datepassed('2000-01-01') == True
    assert filters.datepassed('2040-01-01') == False

    # Test bad input
    assert filters.datepassed('not-a-date') == False
    assert filters.datepassed(2000) == False

def test_filter_render():
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

    # Test adding something to the context
    assert filters.render(context, "{{ var }}{{ var2 }}", var2="a") == "vala"

    # Testing TemplateError
    assert filters.render(context, "{{ invalid template") is None


def test_filter_renderliteral():
    data_dict = {
        "var": "val"
    }

    template = app.jinja_env.from_string("{{ var }}")
    context = template.new_context(vars=data_dict)
    # Testing literal_eval
    liter = filters.renderliteral(context, "['1','2','3']")
    assert isinstance(liter, list)
    assert len(liter) == 3
    assert liter[0] == '1'

    # Testing ValueError
    liter = filters.renderliteral(context, "stringwithoutspaces")
    assert liter == "stringwithoutspaces"
    with raises(ValueError) as verror:
        liter = filters.renderliteral(context, "stringwithoutspaces", False)

    # Testing SyntaxError
    liter = filters.renderliteral(context, "string with spaces")
    assert liter == "string with spaces"
    with raises(SyntaxError) as serror:
        liter = filters.renderliteral(context, "string with spaces", False)

def test_filter_formatedate():
    # Test with valid end date
    res = filters.formatedate("2020-12-31")
    assert res == "December 31st, 2020"
    res = filters.formatedate("2022-01-03")
    assert res == "January 3rd, 2022"
    res = filters.formatedate("8000-01-03")
    assert res == "January 3rd, 8000"

    # Test with indenfinite end date
    res = filters.formatedate("9999-12-31")
    assert res == "Indefinite"
    res = filters.formatedate("")
    assert res == "Indefinite"
    res = filters.formatedate(None)
    assert res == "Indefinite"

    # Test with wrong datatype passed
    res = filters.formatedate(123)
    assert res == "Indefinite"

    # Test wrong format passed
    res = filters.formatedate("abc")
    assert res == "Indefinite"
    res = filters.formatedate("01-01-2020")
    assert res == "Indefinite"

    # Test overriding the default value
    res = filters.formatedate("9999-12-31", "different")
    assert res == "different"

def test_filter_formatiso8601():
    assert filters.formatiso8601("2001-02-28T16:54:29Z") == "2001-02-28"
    assert filters.formatiso8601("2001-02-28T16:54:29-04:00") == "2001-02-28"
    assert filters.formatiso8601("2001-12-31", "%Y") == "2001"
    assert filters.formatiso8601("*") == "Any"
    assert filters.formatiso8601({}) == "Any"
    assert filters.formatiso8601("!!", "%Y", "Unknown") == "Unknown"

def test_filter_sandbug():
    # calling the debug logger
    filters.filter_sandbug("test")

def test_filter_deepcopy():
    child_obj = {'z': 'z'}
    first_obj = {'a': 'b', 'c': child_obj}
    second_obj = filters.deepcopy(first_obj)
    # assert both the dict's contain same values and  do not point to the same memory location
    assert first_obj == second_obj
    assert first_obj is not second_obj
    first_obj['c']['z'] = 'NOT Z'
    # modifying the child object to verify the memeory location is not the same
    assert first_obj != second_obj

def test_filter_solr_getfq():
    query = {
        'q': "frogs",
        'fq': ["dessert:cake", "dessert:pie", "location:East\\ Lansing", "location:St\\ John's", "colon:value:with:colons"]
    }
    # get the filter query as a dict with a list of values
    res = filters.solr_getfq(query)
    assert res == {'dessert': ['cake', 'pie'], 'location': ["East Lansing", "St John's"], "colon": ["value:with:colons"]}

    query = {
        'q': "frogs",
        'fq': "dessert:custard"
    }
    # get the filter query as a dict with a list of values
    res = filters.solr_getfq(query)
    assert res == {'dessert': ['custard']}

    # attempt to get an invalid fq
    query = {
        'q': "frogs",
        'fq': "nocolonhere"
    }
    res = filters.solr_getfq(query)
    assert res == {}

def test_filter_solr_addfq():
    query = {
        'q': "frogs"
    }
    res = filters.solr_addfq(query, 'location', "East Lansing")
    assert res == {'q': "frogs", 'fq': ["location:East\\ Lansing"]}

    # adding multiple times only results in a single entry
    res = filters.solr_addfq(res, 'location', "East Lansing")
    assert res == {'q': "frogs", 'fq': ["location:East\\ Lansing"]}

    query = {
        'q': "frogs",
        'fq': "dessert:cake"
    }

    # adding field and value to the filter query
    res = filters.solr_addfq(query, 'dessert', "pie")
    assert res == {'q': "frogs", 'fq': ["dessert:cake", "dessert:pie"]}

    # test with a 'start' param to make sure it is removed
    query['start'] = 20
    res = filters.solr_addfq(query, 'test', 'coolthing')
    assert res == {'q': "frogs", 'fq': ["dessert:cake", "dessert:pie", "test:coolthing"]}

def test_filter_solr_hasfq():
    query = {
        'q': "frogs",
        'fq': ["dessert:cake", "location:East\\ Lansing"]
    }
    res = filters.solr_hasfq(query, 'location', "East Lansing")
    assert res == True

    query = {
        'q': "frogs",
        'fq': ["dessert:cake", "location:East\\ Lansing"]
    }
    # Pass a non existing field and value to compare with the filter query
    res = filters.solr_hasfq(query, 'dessert', "ice cream")
    assert res == False

    query = {
        'q': "frogs",
        'fq': "dessert:cake"
    }

    # Pass a non existing field and value to compare with the filter query
    res = filters.solr_hasfq(query, 'dessert', "ice cream")
    assert res == False

    # Pass an existing field and value to compare with the filter query
    res = filters.solr_hasfq(query, 'dessert', "cake")
    assert res == True

def test_filter_solr_removefq():
    query = {
        'q': "frogs",
        'fq': ["dessert:cake", "location:East\\ Lansing"]
    }
    res = filters.solr_removefq(query, 'location', "East Lansing")
    assert res == {'q': "frogs", 'fq': ["dessert:cake"]}

    # removing a filterquery that doesn't exist doesn't do anything
    res = filters.solr_removefq(query, 'notafield', "Not a value")
    assert res == {'q': "frogs", 'fq': ["dessert:cake"]}

    query = {
        'q': "frogs",
        'fq': "dessert:cake"
    }
    res = filters.solr_removefq(query, 'dessert', "cake")
    assert res == {'q': "frogs", 'fq': []}

    # test with a 'start' param to make sure it is removed
    query['start'] = 20
    res = filters.solr_removefq(query, 'test', 'coolthing')
    assert res == {'q': "frogs", 'fq': []}

    # TEMP test for fix_preescaped_query
    query = {
        'q': "frogs",
        'fq': ["dessert:(cake OR \"ice cream\")"]
    }
    res = filters.solr_removefq(query, 'dessert', '(cake OR \"ice cream\")')
    assert res == {'q': "frogs", 'fq': []}

def test_filter_totuples():
    example_list = ['xyz', 1, 'abc', 3]
    # test with a list with evenly divisible tuple count
    res = filters.totuples(example_list, 2)
    assert [('xyz', 1), ('abc', 3)] == res

    # test with a list with evenly divisible tuple count
    example_list = ['xyz', 1, 2, 'abc', 3, 4]
    res = filters.totuples(example_list, 3)
    assert [('xyz', 1, 2), ('abc', 3, 4)] == res

    # test with a list with unevenly divisible tuple count
    example_list = ['xyz', 1, 2, 'abc', 3, 4]
    res = filters.totuples(example_list, 4)
    assert [('xyz', 1, 2, 'abc')] == res

def test_filter_todict():
    example_list = ['xyz', 1, 'abc', 3]
    # test with a list with evenly divisible count
    res = filters.todict(example_list)
    assert {'xyz':1, 'abc': 3} == res

    # test with a list with unevenly divisible count
    example_list = ['xyz', 1, 2, 'abc', 3]
    res = filters.todict(example_list)
    assert {'xyz': 1, 2:'abc'} == res

def test_filter_regex_match():
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

def test_filter_regex_sub():
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

def test_filter_getconfig():
    assert filters.filter_getconfig('LOG_LEVEL') == generic.getconfig('LOG_LEVEL')

def test_filter_commafy():
    assert filters.commafy(1234) == "1,234"
    assert filters.commafy(123) == "123"
    assert filters.commafy(1234567) == "1,234,567"
    assert filters.commafy("1234") == ""
    assert filters.commafy("not-numbler") == ""
    assert filters.commafy(['a']) == ""

def test_filter_xpath():
    xmlstr = "<root><elem>Pre <mid>Mid</mid> Tail</elem><elem>Second</elem></root>"
    matched = filters.filter_xpath(xmlstr, "/root/elem")
    assert len(matched) == 2

def test_filter_xpath_by_id():
    xmlstr = "<root><elem id='one'>Pre <mid>Mid</mid> Tail</elem><elem>Second</elem></root>"
    idmap = filters.filter_xpath_by_id(xmlstr, "/root/elem")
    assert idmap == { 'one': "Pre <mid>Mid</mid> Tail" }

def test_json_embedstring():
    assert filters.json_embedstring(r'\"vegetable\ soups\"') == r'\\\"vegetable\\ soups\\\"'
    assert filters.json_embedstring(r'vegetable\ soups') == r'vegetable\\ soups'
    assert filters.json_embedstring({'not-a': "string val"}) == {'not-a': "string val"}

def test_get_descendant():
    data = [
        {
            "key1": ["val-a", "val-b"],
            "key2": ["val-c", "val-d"],
        },
        {
            "key1": ["val-x", "val-y"],
            "key2": "val-z",
        }
    ]

    assert filters.filter_getdescendant(data, "0.key2.1") == "val-d"
    assert filters.filter_getdescendant(data, "0.key2.3") == None
    assert filters.filter_getdescendant(data, "0.key2.3", []) == []

def test_findstartswith():
    data = ["val-a", "val-b", "myteststring"]
    assert filters.findstartswith(data, "val") == "val-a"
    assert filters.findstartswith(data, "mytest") == "myteststring"
    assert filters.findstartswith(data, "doesn't exist") == None
    assert filters.findstartswith("wrong data type", "item") == None

def test_solr_extractrange():
    assert filters.solr_extractrange("no range") == None
    assert filters.solr_extractrange("Only one date [2000-00-00T00:00:00]") == None
    assert filters.solr_extractrange("dates [2000-00-00T00:00:00 TO 2001-00-00T00:00:00]") == ('2000-00-00T00:00:00', '2001-00-00T00:00:00')
    assert filters.solr_extractrange("Another range [9 TO 5]") == ('9', '5')
    assert filters.solr_extractrange("Another range with letters [going TO town]") == ('going', 'town')

def test_solr_facetdates():
    data = [
        "param1=123",
        "param_search=piano",
        "param_date=[2000-01-01T00:00:00Z TO 2001-01-01T00:00:00Z]",
    ]
    results_none = {
        "min": None,
        "max": None,
    }
    results_date = {
        "min": "2000",
        "max": "2001",
    }
    assert filters.solr_facetdates(data, "param1") == results_none
    assert filters.solr_facetdates(data, "param_date") == results_date

def test_indexvaluegreaterthan():
    data_raw = [
        ("param1", 123),
        ("param2", 14, "param3"),
        ("param3", 10),
        ("param4", 1, "param2"),
    ]
    data_over_1 = [
        ("param1", 123),
        ("param2", 14, "param3"),
        ("param3", 10),
    ]
    data_over_10 = [
        ("param1", 123),
        ("param2", 14, "param3"),
    ]
    data_over_14 = [
        ("param1", 123),
    ]
    assert list(filters.filter_indexvaluegreaterthan(data_raw, 1, 0)) == data_raw
    assert list(filters.filter_indexvaluegreaterthan(data_raw, 1, 10)) == data_over_10
    assert list(filters.filter_indexvaluegreaterthan(data_raw, 1, "14")) == data_over_14
    assert list(filters.filter_indexvaluegreaterthan(data_raw, 1)) == data_over_1
    assert list(filters.filter_indexvaluegreaterthan(data_raw, 1, {})) == data_over_1

def test_pluralizer():
    assert filters.filter_pluralizer('term', 1) == 'term'
    assert filters.filter_pluralizer('term', 10) == 'terms'
    assert filters.filter_pluralizer(['term'], 15) == ['term']
    assert filters.filter_pluralizer('term', '10') == 'term'
