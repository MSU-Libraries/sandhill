from sandhill import app
import flask
from sandhill.processors import request
from pytest import raises
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers.response import Response as WerkzeugReponse

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
        'url': 'https://jsonplaceholder.typicode.com/todos/invalid',
        'on_fail': 0
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
        'url': 'https://google.com/',
        'on_fail': 0
    }
    with raises(HTTPException) as http_error:
        url = request.api_json(data)
    assert http_error.type.code == 503

    del data['on_fail']
    assert request.api_json(data) == {}


def test_redirect():
    data_dict = {
        "location": "/go-elsewhere.html",
    }

    # a working redirect
    result = request.redirect(data_dict)
    assert isinstance(result, WerkzeugReponse)
    assert result.headers['Location'] == "/go-elsewhere.html"
    assert result.status_code == 302

    # a working redirect with alternate code
    data_dict['code'] = 301
    result = request.redirect(data_dict)
    assert isinstance(result, WerkzeugReponse)
    assert result.status_code == 301

    # failing to pass a location to the redirect
    with raises(HTTPException) as http_error:
        result = request.redirect({})
    assert http_error.type.code == 500
