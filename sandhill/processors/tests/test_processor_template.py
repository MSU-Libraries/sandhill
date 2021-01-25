'''
Tests for the template processor
'''
from flask import Response as FlaskResponse
from werkzeug.exceptions import HTTPException
from requests.models import Response as RequestsResponse
from pytest import raises
from sandhill import app
from sandhill.processors import template

def test_render():
    '''
    Tests the render function
    '''
    test_resp = FlaskResponse()
    data_dict = {
        "test": test_resp
    }

    # Test for passing it a data set with a FlaskResponse in the given key
    resp = template.render("home.html.j2", "test", **data_dict)
    assert isinstance(resp, FlaskResponse)
    assert resp == test_resp

    # Test passing data without the FlaskResponse
    with app.test_request_context('/home'):
        resp = template.render("home.html.j2", "not_there", **data_dict)
        assert isinstance(resp, str)

    # Test passing in an invalid template
    with app.test_request_context('/home'):
        with raises(HTTPException) as http_exc:
            resp = template.render("note-there.html.j2", "not_there", **data_dict)
        assert http_exc.type.code == 501

    # Test with a syntax error in the template
    with app.test_request_context('/home'):
        with raises(HTTPException) as http_exc:
            resp = template.render("invalid.html.j2", "invalid", **data_dict)
        assert http_exc.type.code == 500
