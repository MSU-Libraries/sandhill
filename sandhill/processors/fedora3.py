import os
from flask import abort
from sandhill.utils.api import api_get
from sandhill import app
from requests import RequestException

def load_datastream(data_dict):
    fedora = None
    allowed_actions = ['view', 'download']
    pid = "{0}:{1}".format(data_dict['view_arg']['namespace'], data_dict['view_arg']['id'])
    data_dict['view_arg']['action'] = data_dict['view_arg']['action'] if data_dict['view_arg']['action'] else 'view'
    if data_dict['view_arg']['action'] not in allowed_actions:
        abort(400)
    try:
        params = {}
        if data_dict['view_arg']['action'] == "download":
            params['download'] = 'true'
        fc_url = os.path.join(app.config['FEDORA_BASE'],
                    "objects/{0}/datastreams/{1}/content".format(pid, data_dict['view_arg']['label']))
        app.logger.info("Connecting to {0}".format(fc_url))
        fedora = api_get(url=fc_url, params=params, stream=True)

        if not fedora.ok:
            app.logger.warning("Call to Fedora Commons returned {0}: {1}".format(fedora.status_code, fc_url))
            abort(fedora.status_code)
    except RequestException as exc:
        app.logger.warning("Call to Fedora Commons failed: {0} \"{1}\"".format(fc_url, exc))
        abort(503)
    return fedora
