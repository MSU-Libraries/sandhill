'''
Tests the main.py route file
'''
import io
from flask import Response as FlaskResponse
from werkzeug.exceptions import HTTPException
from requests.models import Response as RequestsResponse
from pytest import raises
from sandhill import app
from sandhill.routes import main


def test_main():
    '''
    Tests the main function
    '''
    client = app.test_client()

    # test loading a page that has no data to load
    result = client.get('/')
    assert result.status_code == 200

    # test loading a page that does have data to load
    result = client.get('/about')
    assert result.status_code == 200

    # test streaming a page
    result = client.get('/stream')
    assert result.status_code == 200

    # test an invalid page
    result = client.get('/invalid/page/route')
    assert result.status_code == 404

    # test route with invalid data specification
    result = client.get('/invalid-data')
    assert result.status_code == 200

    # test an invalid route config
    result = client.get('/missing')
    assert result.status_code == 404

def test_handle_template():
    '''
    Tests the handle_template function
    '''
    test_resp = FlaskResponse()
    data_dict = {
        "test": test_resp
    }

    # Test for passing it a data set with a FlaskResponse in the given key
    resp = main.handle_template("home.html.j2", "test", **data_dict)
    assert isinstance(resp, FlaskResponse)
    assert resp == test_resp

    # Test passing data without the FlaskResponse
    with app.test_request_context('/home'):
        resp = main.handle_template("home.html.j2", "not_there", **data_dict)
        assert isinstance(resp, str)

    # Test passing in an invalid template
    with app.test_request_context('/home'):
        with raises(HTTPException) as http_exc:
            resp = main.handle_template("note-there.html.j2", "not_there", **data_dict)
        assert http_exc.type.code == 501

def test_handle_stream():
    '''
    Tests the handle_stream function
    '''
    test_resp = RequestsResponse()
    test_resp.raw = io.StringIO("This is a test")
    test_resp.status_code = 200
    test_resp.headers['Content-Type'] = 'application/json'
    data_dict = {
        "test": test_resp
    }

    with app.test_request_context('/home'):
        # Test passing it the correct information
        resp = main.handle_stream("test", **data_dict)
        assert test_resp.status_code == resp.status_code
        assert isinstance(resp, FlaskResponse)
        assert test_resp.headers['Content-Type'] == resp.headers['Content-Type']

        # Test returning a non-OK status code
        test_resp.status_code = 400
        with raises(HTTPException) as http_exc:
            resp = main.handle_stream("test", **data_dict)
        assert http_exc.type.code == 400

        # Test not giving the correct key in data
        with raises(HTTPException) as http_exc:
            resp = main.handle_stream("invalid", **data_dict)
        assert http_exc.type.code == 500

        # Test giving no data in the key
        data_dict["test2"] = None
        with raises(HTTPException) as http_exc:
            resp = main.handle_stream("test2", **data_dict)
        assert http_exc.type.code == 503
