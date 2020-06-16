import requests
import json
from .. import app

def api_get(**kwargs):
    """Perform an API call GET request to return the response object"""
    app.logger.info("API GET call: {0}".format(json.dumps(kwargs)))
    response = requests.get(**kwargs)
    if not response.ok:
        app.logger.info("API GET call returned {0}: {1}".format(response.status_code, response.text))
    return response
