'''
Fedora data processor
'''
import os
from urllib.parse import urlencode
from requests import RequestException
from flask import abort
from sandhill.utils.api import api_get, establish_url
from sandhill.utils.generic import get_config
from sandhill import app

def load_datastream(data_dict, url=None, api_get_function=api_get):
    '''
    Load a requested datastream
    args:
        data_dict(dict): route data and context data
        url(str): Override the fedora URL stored in FEDORA_URL of the configs
        api_get_function(function): function to use to make the Fedora call
    returns:
        Response: the response from Fedora
    '''
    fedora = None
    allowed_actions = ['view', 'download']
    if data_dict['view_args']['action'] not in allowed_actions:
        abort(400)

    url = establish_url(url, get_config('FEDORA_URL', None))
    try:
        params = {}
        params['download'] = 'true' if data_dict['view_args']['action'] == "download" else 'false'
        fc_url = os.path.join(url,
                              "objects/{0}:{1}/datastreams/{2}/content".format(
                                  data_dict['view_args']['namespace'],
                                  data_dict['view_args']['id'],
                                  data_dict['view_args']['label']
                                  )
                              )
        app.logger.debug("Connecting to {0}?{1}".format(fc_url, urlencode(params)))
        fedora = api_get_function(url=fc_url, params=params, stream=True)

        if not fedora.ok:
            app.logger.warning("Call to Fedora Commons returned {0}".format(fedora.status_code))
            abort(fedora.status_code)
    except RequestException as exc:
        app.logger.warning("Call to Fedora Commons failed: {0}".format(exc))
        abort(503)
    except KeyError as exc:
        app.logger.error("Missing url component: {0}".format(exc))
        abort(400)

    return fedora
