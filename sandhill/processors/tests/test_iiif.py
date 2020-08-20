from sandhill.processors import iiif
from requests.models import Response
from pytest import raises
from werkzeug.exceptions import HTTPException
from requests.exceptions import RequestException


def test_load_image():
    data_dict = {
        'view_args': {
            'iiif_path': '/0,0,3777,5523/1889,/0/default.jpg'
            },
        'identifier': 'https%3A%2F%2example.edu%2Fpid'
    }

    # positive response: url is structured correctly, returns expected response
    response = iiif.load_image(data_dict, iiif_url="https://example.edu/iiif", api_get_function=_test_api_get)    
    assert isinstance(response, Response)
    assert response.ok 

    # Test for no url passed in
    response = iiif.load_image(data_dict, iiif_url=None, api_get_function=_test_api_get)    
    assert isinstance(response, Response)
    assert response.ok 

    # Test for invalid iiif_url
    with raises(HTTPException) as http_error:
        response = iiif.load_image(data_dict, iiif_url="invalid:/url/format", api_get_function=_test_api_get)    
    assert http_error.type.code == 400
    
    # Test that fail fails correctly    
    response = iiif.load_image(data_dict, iiif_url="https://example.edu/iiif", api_get_function=_test_api_get_fail)    
    assert isinstance(response, Response)
    assert response.status_code == 500

    # Test that the api service shows correctly as 'unavailable'
    with raises(HTTPException) as http_error:
        response = iiif.load_image(data_dict, iiif_url="https://example.edu/iiif", api_get_function=_test_api_get_unavailable)    
    assert http_error.type.code == 503 

    # Test that call fails when we pass in an invalid data dict
    del data_dict['identifier']
    with raises(HTTPException) as http_error:
        response = iiif.load_image(data_dict, iiif_url="https://example.edu/iiif", api_get_function=_test_api_get)
    assert http_error.type.code == 503


def _test_api_get(url=None, params=None, stream=True):
    """Test function to simulate fedora api call."""
    response = Response()
    response.status_code = 200
    return response

def _test_api_get_fail(url=None, params=None, stream=True):
    """Test function to always fail."""
    response = Response()
    response.status_code = 500
    return response

def _test_api_get_unavailable(url=None, params=None, stream=True):
    """Test function to always fail."""
    raise RequestException()

