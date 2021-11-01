'''
Test the stream processor
'''
import io
from flask import Response as FlaskResponse
from werkzeug.exceptions import HTTPException
from requests.models import Response as RequestsResponse
from pytest import raises
from sandhill import app
from sandhill.processors import stream

def test_stream():
    '''
    Tests the stream function
    '''
    test_resp = RequestsResponse()
    test_resp.raw = io.StringIO("This is a test")
    test_resp.status_code = 200
    test_resp.headers['Content-Type'] = 'application/json'
    test_resp.headers['Range'] = '0-31'
    test_resp.headers['Invalid-Header'] = '10.0.0.10'
    data_dict = {
        "test": test_resp,
        "response": 'test',
        "on_fail": 0
    }

    with app.test_request_context('/home'):
        # Test passing it the correct information
        resp = stream.response(data_dict)
        assert test_resp.status_code == resp.status_code
        assert isinstance(resp, FlaskResponse)
        assert test_resp.headers['Content-Type'] == resp.headers['Content-Type']
        assert test_resp.headers['Range'] == resp.headers['Range']

        # Test valid RequestsResponse, but >= 400 http code
        test_resp.status_code = 401
        del data_dict['on_fail']
        assert stream.response(data_dict) == None

        # Test not a valid RequestResponse
        data_dict["test"] = "string is not allowed"
        assert stream.response(data_dict) == None

        # Test returning a non-OK status code
        data_dict['test'] = test_resp
        data_dict['on_fail'] = 0
        test_resp.status_code = 400
        with raises(HTTPException) as http_exc:
            resp = stream.response(data_dict)
        assert http_exc.type.code == 400

        # Test not giving the correct key in data
        data_dict['response'] = 'invalid'
        with raises(HTTPException) as http_exc:
            resp = stream.response(data_dict)
        assert http_exc.type.code == 503

        # Test giving no data in the key
        data_dict["test2"] = None
        data_dict['response'] = 'test2'
        with raises(HTTPException) as http_exc:
            resp = stream.response(data_dict)
        assert http_exc.type.code == 503

        # Test disallowed header
        assert 'Invalid-Header' not in resp.headers

        # Test missing 'response' key in data_dict
        del data_dict['response']
        with raises(HTTPException) as http_exc:
            resp = stream.response(data_dict)
        assert http_exc.type.code == 500

