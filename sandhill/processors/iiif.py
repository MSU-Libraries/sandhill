'''
Processor for IIIF
'''
import os
from requests.exceptions import RequestException
from sandhill import app, catch
from sandhill.utils.api import api_get, establish_url
from sandhill.utils.generic import get_config
from sandhill.utils.error_handling import dp_abort

@catch(RequestException, "Call to IIIF Server failed: {exc}", abort=503)
def load_image(data_dict, url=None, api_get_function=api_get):
    '''
    Load a IIIF image
    args:
        data_dict(dict): route data where [view_ags][iiif_path] and [identifier] exist
        url(str): Override the IIIF server URL from the default IIIF_BASE in the configs
        api_get_function(function): function to use when making the GET request
    returns:
        image: Requested image from IIIF
    '''
    image = None
    url = establish_url(url, get_config('IIIF_BASE', None))
    if 'iiif_path' in data_dict['view_args'] and 'identifier' in data_dict:
        image = api_get_function(
            url=os.path.join(url, data_dict['identifier'], data_dict['view_args']['iiif_path']),
            stream=True)
    else:
        app.logger.warning("Could not call IIIF Server; missing identifier or iiif_path")
        dp_abort(500)

    if not image.ok:
        app.logger.debug("Call to IIIF Server returned {0}".format(image.status_code))
        dp_abort(image.status_code)
        image = None
    return image
