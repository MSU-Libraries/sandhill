"""
Dummy functions for use in unit tests.
"""
from requests.models import Response
from requests.exceptions import RequestException
import json
import io

def _test_api_get(url=None, params=None, stream=True, headers=None):
    """Test function to simulate successfull API call."""
    response = Response()
    response.status_code = 200
    return response

def _test_api_get_json(url=None, params=None, stream=True, headers=None):
    """Test function to simulate successful API call returning JSON."""
    response = Response()
    response._content = b'{"test":["test"]}'
    response.raw = io.BytesIO(response._content)
    response.status_code = 200
    return response

def _test_api_get_json_error(url=None, params=None, stream=True, headers=None):
    """Test function to simulate bad request API call returning JSON."""
    response = Response()
    response._content = b'{"error":"test"}'
    response.raw = io.BytesIO(response._content)
    response.status_code = 400
    return response

def _test_api_get_fail(url=None, params=None, stream=True, headers=None):
    """Test function to simulate internal server error API call."""
    response = Response()
    response.status_code = 500
    return response

def _test_api_get_unavailable(url=None, params=None, stream=True, headers=None):
    """Test function to raise a requests.RequestException."""
    raise RequestException()

def _test_api_get_json_params(url=None, params=None, stream=True, headers=None):
    """Test function to simulate successful API call returning JSON overloading params."""
    response = Response()
    response._content = json.dumps(params).encode()
    response.status_code = 200
    return response

def _test_api_get_redirect(url=None, params=None, stream=True, headers=None):
    """Test function to simulate an API call returning 300."""
    response = Response()
    response.raw = io.BytesIO(b'')
    response.status_code = 300
    return response
