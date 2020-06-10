import logging
import requests
import json

def api_get(url, query):
    """Perform an API call GET request to return the response object"""
    logging.info("API GET call: {0}".format(url, json.dumps(query)))
    response = requests.get(url, params=query)
    if not response.ok:
        logging.info("API GET call returned {0}: {1}".format(response.status_code, response.text))
    return response
