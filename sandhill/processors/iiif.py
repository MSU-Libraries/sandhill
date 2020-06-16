import requests

def load_image(data_dict):
    image = None
    if 'url' in data_dict and isinstance(data_dict['url'], str):
        image = requests.get(data_dict['url'], stream=True)
    return image
