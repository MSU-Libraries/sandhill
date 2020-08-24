import os
from sandhill.utils.api import api_get
from sandhill import app
from flask import abort
from sandhill.utils.api import establish_url
from sandhill.utils.generic import ifnone
from requests.exceptions import RequestException


def load_image(data_dict, url=None, api_get_function=api_get):
    image = None
    url = establish_url(url, ifnone(app.config, 'IIIF_BASE', None))
    try:
        if 'iiif_path' in data_dict['view_args'] and 'identifier' in data_dict:
            image = api_get_function(url=os.path.join(url, data_dict['identifier'], data_dict['view_args']['iiif_path']),
                        stream=True)
        else:
            app.logger.warning("Could not call IIIF Server; missing identifier or iiif_path")
            abort(500)

        if not image.ok:
            app.logger.debug("Call to IIIF Server returned {0}".format(image.status_code))
    except RequestException as exc:
        app.logger.warning("Call to IIIF Server failed: {0}".format(exc))
        abort(503)
    return image
