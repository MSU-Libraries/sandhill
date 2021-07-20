'''
Test the generic processor
'''
import io
from flask import Response as FlaskResponse
from requests.models import Response as RequestsResponse
from pytest import raises
from sandhill.processors import generic

def test_replace():
    '''
    Tests the stream function
    '''
    # Testing with JSON
    test_data = [
        { "key1": 1 },
        { "key2": 2.0 }
    ]
    data_dict = {
        "name": "json",
        "json": test_data,
        "old": "2.0",
        "new": '"two.zero"'
    }

    new_data = generic.replace(data_dict)
    assert isinstance(new_data, list)
    assert new_data == [{ "key1": 1 }, { "key2": "two.zero" }]

    # Testing with Requests library response
    test_resp = RequestsResponse()
    test_resp.raw = io.BytesIO(b'{"test1": "value_one", "test2": [2]}')
    test_resp.status_code = 200
    test_resp.headers['Content-Type'] = 'application/json'
    data_dict = {
        "name": "json",
        "json": test_resp,
        "old": '"test2": [2]',
        "new": '"test3": "three"'
    }

    new_resp = generic.replace(data_dict)
    assert isinstance(new_resp, RequestsResponse)
    assert new_resp.content == b'{"test1": "value_one", "test3": "three"}'

    # Testing with failed Requests library response
    test_resp = RequestsResponse()
    test_resp.raw = io.BytesIO(b'404 Not Found')
    test_resp.status_code = 404
    test_resp.headers['Content-Type'] = 'text/plain'
    data_dict = {
        "name": "json",
        "json": test_resp,
        "old": '"test2": [2]',
        "new": '"test3": "three"'
    }

    new_resp = generic.replace(data_dict)
    assert isinstance(new_resp, RequestsResponse)
    assert new_resp.content == b'404 Not Found'
