from ..utils.api import api_get
from .. import app

def load_image(data_dict):
    image = None
    if 'view_arg' in data_dict and 'iiif_path' in data_dict['view_arg'] and 'url' in data_dict:
        image = api_get(url=app.config['IIIF_BASE'] + "/" + data_dict['url'] + "/" +  data_dict['view_arg']['iiif_path'], stream=True)
    return image
