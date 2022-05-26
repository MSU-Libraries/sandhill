'''
Processor for IIIF
'''
import os
from requests.exceptions import RequestException
from sandhill import app, catch
from sandhill.utils.api import api_get, establish_url
from sandhill.utils.generic import getconfig
from sandhill.utils.error_handling import dp_abort

@catch(RequestException, "Call to IIIF Server failed: {exc}", abort=503)
def load_image(data, url=None, api_get_function=api_get):
    '''
    Load and return a IIIF image
    Args:
        data (dict): route data where [view_ags][iiif_path] and [identifier] exist
        url (str): Override the IIIF server URL from the default IIIF_BASE in the configs
        api_get_function (function): function to use when making the GET request
    Returns:
        (requests.Response|None): Requested image from IIIF, or None on failure.
    Raises:
        (HTTPException): On failure if `on_fail` is set.
    '''
    image = None
    url = establish_url(url, getconfig('IIIF_BASE', None))
    if 'iiif_path' in data['view_args'] and 'identifier' in data:
        image = api_get_function(
            url=os.path.join(url, data['identifier'], data['view_args']['iiif_path']),
            stream=True)
    else:
        app.logger.warning("Could not call IIIF Server; missing identifier or iiif_path")
        dp_abort(500)

    if not image.ok:
        app.logger.debug(f"Call to IIIF Server returned {image.status_code}")
        dp_abort(image.status_code)
        image = None
    return image
