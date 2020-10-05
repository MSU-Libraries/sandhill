import os
from pytest import raises
from werkzeug.exceptions import HTTPException
from sandhill.processors import solr
from flask import Response as FlaskResponse
from requests.exceptions import RequestException
from sandhill.utils.test import _test_api_get, _test_api_get_fail, _test_api_get_unavailable, _test_api_get_json, _test_api_get_json_error
from sandhill import app

def test_select():
    data_dict = {
        'params' : {},
        'dummy': 'value'
    }

    # Test for successful response
    response = solr.select(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_json)
    assert isinstance(response, dict)

    # Test that a missing Solr URL fails
    with raises(HTTPException) as http_error:
        response = solr.select(data_dict, url=None, api_get_function=_test_api_get_json)
    assert http_error.type.code == 400

    # Test that a missing request fails correctly
    with raises(HTTPException) as http_error:
        result = solr.select(data_dict)
    assert http_error.type.code == 400

    # Test with a bad URL
    with raises(HTTPException) as http_error:
        response = solr.select(data_dict, url="not_a_url", api_get_function=_test_api_get_json)
    assert http_error.type.code == 400

    # Test a failed call
    with raises(HTTPException) as http_error:
        response = solr.select(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_fail)
    assert http_error.type.code == 500

    # Test an unavailable call
    with raises(HTTPException) as http_error:
        response = solr.select(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_unavailable)
    assert http_error.type.code == 503

    # Test missing params
    del data_dict["params"]
    with raises(HTTPException) as http_error:
        response = solr.select(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_fail)
    assert http_error.type.code == 400

def test_select_record():
    data_dict = {
        'params' : {},
        'record_keys': 'test'
    }

    # Test for successful response
    response = solr.select_record(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_json)
    assert isinstance(response, str)
    assert response

    # Test that a missing request fails correctly
    with raises(HTTPException) as http_error:
        result = solr.select_record(data_dict)
    assert http_error.type.code == 400

    # Test that a missing data dict fails correctly
    with raises(HTTPException) as http_error:
        result = solr.select_record(data_dict={}, url="https://test.example.edu", api_get_function=_test_api_get_json)
    assert http_error.type.code == 400

    # Test that no records_keys provided will return none
    del data_dict["record_keys"]
    response = solr.select_record(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_json)
    assert response is None

    # Test a Solr error
    with raises(HTTPException) as http_error:
        response = solr.select_record(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_json_error)
    assert http_error.type.code == 400

    # Test if a dictionary is not returned
    with raises(HTTPException) as http_error:
        result = solr.select_record(data_dict, url="https://test.example.edu", api_get_function=_test_api_get)
    assert http_error.type.code == 503

def test_search():
    data_dict = {
        "name": "search",
        "processor": "solr.search",
        "paths": [ 'search_configs/main.json' ]
    }

    # Test for successful request with a dict response
    with app.test_request_context('/search'):
        response = solr.search(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_json)
        assert isinstance(response, dict)
        assert response

    # Test for successful request with a jsonify'ed response
    with app.test_request_context('/search.json'):
        response = solr.search(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_json)
        assert isinstance(response, FlaskResponse)
        assert response.status_code == 200

    # Test for passing a url parameter to overrride default
    with app.test_request_context('/search?q=changed&start=20'):
        response = solr.search(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_json)
        assert isinstance(response, dict)
        assert response

    # Test for missing solr params
    with app.test_request_context('/search'):
        data_dict['paths'] = [ 'search_configs/invalid.json' ]
        with raises(HTTPException) as http_error:
            response = solr.search(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_json)
        assert http_error.type.code == 500

    # Test for missing paths in data_dict
    del data_dict['paths']
    with app.test_request_context('/search.json'):
        with raises(HTTPException) as http_error:
            response = solr.search(data_dict, url="https://test.example.edu", api_get_function=_test_api_get_json)
        assert http_error.type.code == 500
    data_dict["paths"] = [ 'search_configs/main.json' ]
