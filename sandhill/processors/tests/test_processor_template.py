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
        "test": test_resp,
        "file": "home.html.j2"
    }
    
    # Test passing data without the FlaskResponse
    with app.test_request_context('/home'):
        resp = template.render(data_dict)
        assert isinstance(resp, FlaskResponse)

    # Test passing in an invalid template
    data_dict["file"] = "not-there-file.html.j2"
    with app.test_request_context('/home'):
        with raises(HTTPException) as http_exc:
            resp = template.render(data_dict)
        assert http_exc.type.code == 501

    # Test with a syntax error in the template
    data_dict["file"] = "invalid.html.j2"
    with app.test_request_context('/home'):
        with raises(HTTPException) as http_exc:
            resp = template.render(data_dict)
        assert http_exc.type.code == 500

    # Test a template render where a file was not given 
    del data_dict["file"]
    with app.test_request_context('/home'):
        with raises(HTTPException) as http_exc:
            resp = template.render(data_dict)
        assert http_exc.type.code == 500 

def test_render_string():
    data_dict = {
        'processor': 'template.render_string',
        'name': 'datastream_label',
        'test_var': 'test_val',
        'value': '{{ test_var }}',
        'on_fail': 500
    }

    # Test for positive scenario
    evaluation = template.render_string(data_dict)
    assert isinstance(evaluation, str)
    assert evaluation == 'test_val'

    # Test for invalid template passed
    data_dict['value'] = "{{ forgot to close"
    evaluation = template.render_string(data_dict)
    assert evaluation is None

    # Test for invalid variable in valid jinja
    data_dict['value'] = "{{ invalid_var_name }}"
    evaluation = template.render_string(data_dict)
    assert isinstance(evaluation, str)
    assert evaluation == ''

    # Test not providing a 'value'
    del data_dict['value']
    evaluation = template.render_string(data_dict)
    assert evaluation is None
