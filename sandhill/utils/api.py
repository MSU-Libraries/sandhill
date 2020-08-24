import validators
import requests
import json
from flask import abort
from sandhill import app

def api_get(**kwargs):
    """Perform an API call GET request to return the response object"""
    app.logger.debug("API GET call: {0}".format(json.dumps(kwargs)))
    response = requests.get(**kwargs)
    if not response.ok:
        app.logger.warning("API GET call returned {0}: {1}".format(response.status_code, response.text))
    return response

def establish_url(url, fallback):
    url = url if url else fallback
    if not url or not validators.url(url):
        abort(400)
    return url
