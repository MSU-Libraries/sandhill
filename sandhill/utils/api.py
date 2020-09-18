import validators
import requests
import json
from flask import abort
from sandhill import app

def api_get(**kwargs):
    """Perform an API call GET request to return the response object

    kwargs:
        url (str): required for the function to not raise an error
        params (dict): parameters to pass with the url
        (various): any arguments accepted by requests.get
    raises:
        RequestException (exception): Raised if the get function cannot return a response.
    """
    app.logger.debug("API GET call: {0}".format(json.dumps(kwargs)))
    response = requests.get(**kwargs)
    if not response.ok:
        app.logger.warning("API GET call returned {0}: {1}".format(response.status_code, response.text))
    return response

def establish_url(url, fallback):
    """Set url to fallback if url is none; check for valid url.

    args:
        url(str): valid url
        fallback(str): valid url to fallback to if url is none
    raises:
        HTTPException(werkzeurg.exceptions): raised if url is not valid.
    """
    url = url if url else fallback
    if not url or not validators.url(url):
        abort(400)
    return url

