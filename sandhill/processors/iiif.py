import os
from sandhill.utils.api import api_get
from sandhill import app
import validators
from flask import abort
from sandhill.utils.generic import ifnone 
from requests.exceptions import RequestException


def load_image(data_dict, iiif_url=None, api_get_function=api_get):
    image = None
    if not iiif_url:
        iiif_url = ifnone (app.config, 'IIIF_BASE', None)
    if not iiif_url or not validators.url(iiif_url):
        abort(400)
    try: 
        if 'iiif_path' in data_dict['view_args'] and 'identifier' in data_dict:
            image = api_get_function(url=os.path.join(iiif_url, data_dict['identifier'], data_dict['view_args']['iiif_path']), 
                        stream=True)
        else:
            app.logger.warning("Could not call IIIF Server; missing identifier or iiif_path")
            abort(503)

        if not image.ok:
            app.logger.debug("Call to IIIF Server returned {0}".format(image.status_code))
    except RequestException as exc:
        app.logger.warning("Call to IIIF Server failed: {0}".format(exc))
        abort(503)
    return image
