'''
Functionality to support API calls.
'''
from urllib.parse import urlparse
import requests
from requests_futures.sessions import FuturesSession
from flask import abort
from sandhill import app

def api_get(**kwargs):
    """
    Perform an API call using `requests.get()` and return the response object. This function adds \
    logging surrounding the call. \n
    Args:
        **kwargs (dict): Arguments to [`requests.get()`](#TODO) \n
    Raises:
        requests.RequestException: If the call cannot return a response. \n
    """
    if "timeout" not in kwargs:
        kwargs["timeout"] = 10
    app.logger.debug(f"API GET arguments: {kwargs}")
    response = requests.get(**kwargs)   # pylint: disable=missing-timeout
    app.logger.debug(f"API GET called: {response.url}")
    if not response.ok:
        app.logger.warning(
            f"API GET call returned {response.status_code}: {response.text}"
        )
    return response

def api_get_multi(requests_kwargs):
    """
    Perform multiple API calls in parellel using futures, returning a list \
    of responses. \n
    Args:
        requests_kwargs (list of dict): Each arguments to [`requests.get()`] \n
    Returns:
        A generator yielding response objects \n
    """
    def request_futures(requests_kwargs):
        futures = []
        with FuturesSession() as session:
            for kwargs in requests_kwargs:
                if "timeout" not in kwargs:
                    kwargs["timeout"] = 10
                futures.append(session.get(**kwargs))
            for future in futures:
                yield future.result()

    return request_futures(requests_kwargs)

def establish_url(url, fallback):
    """
    Set URL to fallback if provided URL is none; also checks the URL validity. \n
    Args:
        url (str): A possible URL. \n
        fallback (str): A secondary URL to fallback to if `url` is None. \n
    raises:
        werkzeurg.exceptions.HTTPException: If URL to be returned is not a valid formatted URL. \n
    """
    url = url if url else fallback
    try:
        parsed = urlparse(url)
        if not url or not all([parsed.scheme, parsed.netloc]):
            raise ValueError
    except ValueError:
        app.logger.debug(f"URL provided is not valid: {url}")
        abort(400)
    return url
