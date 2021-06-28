from sandhill import app
import flask
from sandhill.processors import request
from pytest import raises
from werkzeug.exceptions import HTTPException

def test_get_url_components():
    data_dict = {}

    # testing a basic path to make sure url components are collected, assembled, passed correctly
    with app.test_request_context('/etd/1000'):
        result = request.get_url_components(data_dict)
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
        result = request.get_url_components(data_dict)
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
        result = request.get_url_components(data_dict)

def test_api_json():
    data = {
        'url': 'https://jsonplaceholder.typicode.com/todos'
    }
    resp = request.api_json(data)
    assert isinstance(resp, list)
    assert len(resp) == 200
    assert resp[0]['title'] == "delectus aut autem"

    # non 200 status
    data = {
        'url': 'https://jsonplaceholder.typicode.com/todos/invalid'
    }
    with raises(HTTPException) as http_error:
        url = request.api_json(data)
    assert http_error.type.code == 404

    # request exception
    data = {
        'url': 'invalid_url'
    }
    with raises(HTTPException) as http_error:
        url = request.api_json(data)
    assert http_error.type.code == 503

    # bad json
    data = {
        'url': 'https://google.com/'
    }
    with raises(HTTPException) as http_error:
        url = request.api_json(data)
    assert http_error.type.code == 503
