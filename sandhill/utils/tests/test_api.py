from sandhill import app
from sandhill.utils import api

def test_api_get():
    # TODO -- to be reviewed by the group

    # test a valid url
    response = api.api_get(url="https://www.google.com")
    assert response.status_code == 200
    
    # test a valid url with query args
    response = api.api_get(url="https://www.google.com/search", params= { "q": "test"})
    assert response.status_code == 200
    assert response.url == "https://www.google.com/search?q=test"

    # test an invalid url
    response = api.api_get(url="https://www.google.com/invalidpagepath")
    assert response.status_code == 404
