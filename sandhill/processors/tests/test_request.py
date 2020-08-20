from sandhill import app
import flask
from sandhill.processors import request
from pytest import raises

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
        
