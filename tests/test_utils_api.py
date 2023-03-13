from sandhill import app
from sandhill.utils import api
from pytest import raises
from requests.exceptions import RequestException
from werkzeug.exceptions import HTTPException

def test_api_get():
    # test a valid url
    response = api.api_get(url="https://www.google.com")
    assert response.status_code == 200

    # test a valid url with query args
    response = api.api_get(url="https://www.google.com/search", params= { "q": "test"})
    assert response.status_code == 200
    assert response.url == "https://www.google.com/search?q=test"

    # test a valid url with query args in url argument
    response = api.api_get(url="https://www.google.com/search?q=test")
    assert response.status_code == 200
    assert response.url == "https://www.google.com/search?q=test"

    # test an invalid url
    response = api.api_get(url="https://www.google.com/invalidpagepath")
    assert response.status_code == 404

    # Test completely false url
    with raises(RequestException):
        response = api.api_get(url="not_a_url")

    # Test non-json serializable kwarg
    with raises(TypeError):
        response = api.api_get(set_not_list={1, 2, 3})

def test_establish_url():
    # Test valid url
    url = api.establish_url("https://www.google.com", "fallback")
    assert url == "https://www.google.com"

    # Test fallback
    url = api.establish_url("", "https://www.google.com")
    assert url == "https://www.google.com"

    # Test non Internet URL
    url = api.establish_url("http://fedora:8080/fedora", "fallback")
    assert url == "http://fedora:8080/fedora"

    # Test invalid url
    with raises(HTTPException) as http_error:
        url = api.establish_url(None, "not_a_url")
    assert http_error.type.code == 400

