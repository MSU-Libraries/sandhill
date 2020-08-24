import os
from pytest import raises
from collections import OrderedDict
from sandhill.processors import file
from sandhill import app
from werkzeug.exceptions import HTTPException

def test_load_json():
    app.instance_path = os.path.join(app.root_path, "test_instance/")

    # Test loading config successfully
    data_dict = {
        'paths': [ 'route_configs/search.json' ]
    }
    file_data = file.load_json(data_dict)
    assert isinstance(file_data, OrderedDict)
    assert file_data

    # Test loading file where the first file isn't there
    data_dict = {
        'paths': [ 'invalid/test.json', 'route_configs/search.json' ]
    }
    file_data = file.load_json(data_dict)
    assert isinstance(file_data, OrderedDict)
    assert file_data

    # Test loading an invalid file
    data_dict = {
        'paths': [ 'invalid/test.json' ]
    }
    file_data = file.load_json(data_dict)
    assert isinstance(file_data, OrderedDict)
    assert not file_data


def test_load_matched_json():
    app.instance_path = os.path.join(app.root_path, "test_instance/")

    # Test matching etd config file successfully
    data_dict = {
        'location': 'metadata_configs_1',
        'view_args': {
            'namespace': 'etd'
        },
        'item': {
            'model_type': 'info:fedora/islandora:sp_pdf'
        }
    }
    file_data = file.load_matched_json(data_dict)
    assert isinstance(file_data, dict)
    assert file_data
    assert 'test_filename' in file_data
    assert file_data['test_filename'] == "etd.json"

    # Test loading directory with invalid match conditions
    data_dict = {
        'location': 'metadata_configs_2',
        'view_args': {
            'namespace': 'etd'
        },
        'item': {
            'model_type': 'info:fedora/islandora:sp_pdf'
        }
    }
    file_data = file.load_matched_json(data_dict)
    assert not isinstance(file_data, dict)
    assert not file_data

    # Testing the on_fail functionality in load_matched_json when the config path is invalid
    data_dict['location'] = "metadata_config_invalid_path"
    data_dict['on_fail'] = 404
    file_data = file.load_matched_json(data_dict)
    assert file_data is None    # expect None return, as base processor will throw the abort