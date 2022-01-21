'''
Processor for requests
'''
from json.decoder import JSONDecodeError
import requests
from requests.exceptions import RequestException
from flask import abort, redirect as FlaskRedirect
from sandhill import app, catch
from sandhill.utils.error_handling import dp_abort

@catch(RequestException, "Call to {data_dict[url]} returned {exc}.", abort=503)
def api_json(data_dict):
    '''
    Make a call to an API and return the response content as JSON
    '''
    method = data_dict['method'] if 'method' in data_dict else 'GET'
    app.logger.debug(f"Connecting to {data_dict['url']}")
    response = requests.request(method=method, url=data_dict["url"])

    if not response.ok:
        app.logger.warning(f"Call to {data_dict['url']} returned a non-ok status code: " \
                           f"{response.status_code}. {response.__dict__}")
        if 'on_fail' in data_dict:
            abort(response.status_code if data_dict['on_fail'] == 0 else data_dict['on_fail'])

    try:
        return response.json()
    except JSONDecodeError:
        app.logger.warning(f"Call returned from {data_dict['url']} that was not JSON.")
        dp_abort(503)
        return {}

@catch(KeyError, "Processor request.redirect called without a 'location' given.", abort=500)
def redirect(data_dict):
    '''
    Redirect request to another url
    '''
    code = data_dict['code'] if 'code' in data_dict else 302
    return FlaskRedirect(data_dict['location'], code=code)
