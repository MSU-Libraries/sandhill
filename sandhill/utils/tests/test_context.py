from pytest import raises
import flask
from sandhill import app
from sandhill.utils import context

def test_list_custom_context_processors():
    assert context.list_custom_context_processors() == [
        'debug',
        'strftime',
        'sandbug',
        'urlcomponents'
    ]

def test_context_processors():
    ctx = context.context_processors()

    assert isinstance(ctx['debug'], bool)
    assert ctx['strftime']('%Y-%m', '2021-08-31') == '2021-08'
    assert ctx['sandbug']('Test for sandbug context processor.') == None

def test_urlcomponents_context_processor():
    ctx = context.context_processors()

    # testing a basic path to make sure url components are collected, assembled, passed correctly
    with app.test_request_context('/etd/1000'):
        app.preprocess_request()
        result = ctx['urlcomponents']()
        assert isinstance(result, dict)

        assert result['path'] == '/etd/1000'
        assert result['full_path'] == '/etd/1000?'
        assert result['base_url'] == flask.request.url_root + 'etd/1000'
        assert result['url'] == flask.request.url_root + 'etd/1000'
        assert result['url_root'] == flask.request.url_root
        assert isinstance(result['query_args'], dict)
        assert not result['query_args']

    # testing a path with a query to make sure the parts are structured correctly
    with app.test_request_context('/search?q=frogs&fq=absek&fq=chocolate'):
        app.preprocess_request()
        result = ctx['urlcomponents']()
        assert isinstance(result, dict)

        assert result['path'] == '/search'
        assert result['full_path'] == '/search?q=frogs&fq=absek&fq=chocolate'
        assert result['base_url'] == flask.request.url_root + 'search'
        assert result['url'] == flask.request.url_root + 'search?q=frogs&fq=absek&fq=chocolate'
        assert isinstance(result['query_args'], dict)
        assert 'q' in result['query_args']
        assert result['query_args']['q'] == ['frogs']
        assert len(result['query_args']) == 2

        assert 'fq' in result['query_args']
        assert result['query_args']['fq'] == ['absek','chocolate']

    # testing that a missing request fails correctly
    with raises(RuntimeError) as run_error:
        result = ctx['urlcomponents']()
