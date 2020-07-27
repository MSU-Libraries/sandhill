import os
from ..utils.api import api_get
from .. import app

def load_image(data_dict):
    image = None
    if 'iiif_path' in data_dict['view_args'] and 'identifier' in data_dict:
        image = api_get(url=os.path.join(app.config['IIIF_BASE'], data_dict['identifier'], data_dict['view_args']['iiif_path']), 
                        stream=True)
    return image
