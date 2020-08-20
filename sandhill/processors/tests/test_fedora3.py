from pytest import raises
from werkzeug.exceptions import HTTPException
from sandhill.processors import fedora3
from requests.models import Response
from requests.exceptions import RequestException


def test_conditions():
    data_dict = {
        "view_args": {
            "action": "view",
            "namespace": "etd",
            "id": "100",
            "label": "TN"
        }
    }
    # Test for successful response
    response = fedora3.load_datastream(data_dict, fedora_url="https://test.example.edu", api_get_function=_test_api_get)
    assert isinstance(response, Response)
    assert response.ok

    # Test for successful response with 'download' action
    data_dict["view_args"]["action"] = "download"
    response = fedora3.load_datastream(data_dict, fedora_url="https://test.example.edu", api_get_function=_test_api_get)
    assert isinstance(response, Response)
    assert response.ok

    # Test for invalid 'action' setting.
    data_dict["view_args"]["action"] = "Invalid"
    with raises(HTTPException) as http_error:
        response = fedora3.load_datastream(data_dict, fedora_url="https://test.example.edu", api_get_function=_test_api_get)
    assert http_error.type.code == 400

    # Test for invalid fedora_url
    data_dict["view_args"]["action"] = "download"
    with raises(HTTPException) as http_error:
        response = fedora3.load_datastream(data_dict, fedora_url="invalid url", api_get_function=_test_api_get)
    assert http_error.type.code == 400

    # Test for invalid fedora_url
    with raises(HTTPException) as http_error:
        response = fedora3.load_datastream(data_dict, fedora_url=None, api_get_function=_test_api_get)
    assert http_error.type.code == 400

    # Test for failed call to fedora
    with raises(HTTPException) as http_error:
        response = fedora3.load_datastream(data_dict, fedora_url="https://test.example.edu", api_get_function=_test_api_get_unavailable)
    assert http_error.type.code == 503

    # Test for non-503 fedora call exception
    with raises(HTTPException) as http_error:
        response = fedora3.load_datastream(data_dict, fedora_url="https://test.example.edu", api_get_function=_test_api_get_fail)
    assert http_error.type.code == 500

    # Test for missing url parameter 'namespace'
    del data_dict["view_args"]["namespace"]
    with raises(HTTPException) as http_error:
        response = fedora3.load_datastream(data_dict, fedora_url="https://test.example.edu", api_get_function=_test_api_get)
    assert http_error.type.code == 400



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
