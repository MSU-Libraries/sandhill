'''
Processor for requests
'''
from json.decoder import JSONDecodeError
import requests
from requests.exceptions import RequestException
from flask import abort, redirect as FlaskRedirect
from sandhill import app, catch
from sandhill.utils.error_handling import dp_abort

@catch(RequestException, "Call to {data[url]} returned {exc}.", abort=503)
def api_json(data):
    '''
    Make a call to an API and return the response content as JSON.
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
            * `url` _str_: The URL to make the API call to.\n
            * `method` _str, optional_: The HTTP method to use.\n
                Default: `"GET"`
    Returns:
        (dict): The JSON response from the API call
    Raises:
        (HTTPException): On failure if `on_fail` is set.
    '''
    method = data['method'] if 'method' in data else 'GET'
    app.logger.debug(f"Connecting to {data['url']}")
    response = requests.request(method=method, url=data["url"])

    if not response.ok:
        app.logger.warning(f"Call to {data['url']} returned a non-ok status code: " \
                           f"{response.status_code}. {response.__dict__}")
        if 'on_fail' in data:
            abort(response.status_code if data['on_fail'] == 0 else data['on_fail'])

    try:
        return response.json()
    except JSONDecodeError:
        app.logger.warning(f"Call returned from {data['url']} that was not JSON.")
        dp_abort(503)
        return {}

@catch(KeyError, "Processor request.redirect called without a 'location' given.", abort=500)
def redirect(data):
    '''
    Trigger a redirect response to specified url.
    Args:
        data (dict): Processor arguments and all other data loaded from previous data processors.\n
        * `location` _str_: URL to redirect client to.\n
        * `code` _int, optional_: HTTP status code to redirect with. Default: 302
    Returns:
        (flask.Response): The flask response object with the included redirect.
    Raises:
        (HTTPException): If the `location` key is not present.
    '''
    code = data['code'] if 'code' in data else 302
    return FlaskRedirect(data['location'], code=code)
