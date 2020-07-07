from urllib.parse import urlencode, urljoin
from flask import abort
from sandhill.utils.api import api_get
from sandhill import app
from requests import RequestException

def load_datastream(data_dict):
    fedora = None
    allowed_actions = ['view', 'download']
    if data_dict['view_arg']['action'] not in allowed_actions:
        abort(400)
    try:
        params = {}
        params['download'] = 'true' if data_dict['view_arg']['action'] == "download" else 'false'
        fc_url = urljoin(app.config['FEDORA_BASE'],
                        "objects/{0}:{1}/datastreams/{2}/content".format(
                        data_dict['view_arg']['namespace'],
                        data_dict['view_arg']['id'],
                        data_dict['view_arg']['label'])
                    )
        app.logger.debug("Connecting to {0}?{1}".format(fc_url, urlencode(params)))
        fedora = api_get(url=fc_url, params=params, stream=True)

        if not fedora.ok:
            app.logger.warning("Call to Fedora Commons returned {0}".format(fedora.status_code))
            abort(fedora.status_code)
    except RequestException as exc:
        app.logger.warning("Call to Fedora Commons failed: {1}".format(exc))
        abort(503)
    return fedora
