from requests.models import Response
from requests.exceptions import RequestException

def _test_api_get(url=None, params=None, stream=True):
    """Test function to simulate solr api call."""
    response = Response()
    response.status_code = 200
    return response

def _test_api_get_json(url=None, params=None, stream=True):
    """Test function to simulate solr api call."""
    response = Response()
    response._content = b'{"test":["test"]}'
    response.status_code = 200
    return response

def _test_api_get_json_error(url=None, params=None, stream=True):
    """Test function to simulate solr api call."""
    response = Response()
    response._content = b'{"error":"test"}'
    response.status_code = 400
    return response

def _test_api_get_fail(url=None, params=None, stream=True):
    """Test function to always fail."""
    response = Response()
    response.status_code = 500
    return response

def _test_api_get_unavailable(url=None, params=None, stream=True):
    """Test function to always fail."""
    raise RequestException()
