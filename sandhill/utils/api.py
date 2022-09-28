'''
Functionality to support API calls.
'''
import validators
import requests
from flask import abort
from sandhill import app

def api_get(**kwargs):
    """
    Perform an API call using `requests.get()` and return the response object. This function adds
    logging surrounding the call.
    Args:
        **kwargs (dict): Arguments to [`requests.get()`](#TODO)
    Raises:
        requests.RequestException: If the call cannot return a response.
    """
    if "timeout" not in kwargs:
        kwargs["timeout"] = 8
    app.logger.debug(f"API GET arguments: {kwargs}")
    response = requests.get(**kwargs)
    app.logger.debug(f"API GET called: {response.url}")
    if not response.ok:
        app.logger.warning(
            f"API GET call returned {response.status_code}: {response.text}"
        )
    return response

def establish_url(url, fallback):
    """
    Set URL to fallback if provided URL is none; also checks the URL validity.
    Args:
        url (str): A possible URL.
        fallback (str): A secondary URL to fallback to if `url` is None.
    raises:
        werkzeurg.exceptions.HTTPException: If URL to be returned is not a valid formatted URL.
    """
    url = url if url else fallback
    if not url or not validators.url(url):
        app.logger.debug(f"Api url provided is not valid. Url: {url}")
        abort(400)
    return url
