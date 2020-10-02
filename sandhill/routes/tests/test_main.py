import os
from sandhill import app
from flask import Response as FlaskResponse
from pytest import raises
from werkzeug.exceptions import HTTPException
from sandhill.routes import main


def test_main():
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
        with raises(HTTPException) as http_exc:
            resp = main.handle_template("note-there.html.j2", "not_there", **data_dict)
        assert http_exc.type.code == 501

def test_handle_stream():
    pass # TODO
