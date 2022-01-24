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
    Make a call to an API and return the response content as JSON
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
    Redirect request to another url
    '''
    code = data['code'] if 'code' in data else 302
    return FlaskRedirect(data['location'], code=code)
