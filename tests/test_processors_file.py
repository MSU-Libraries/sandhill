import os
from pytest import raises
from requests.models import Response as RequestsResponse
from collections import OrderedDict
from sandhill.processors import file
from sandhill import app
from werkzeug.exceptions import HTTPException

def test_load_json():
    # Test loading config successfully
    data_dict = {
        'paths': [ 'config/routes/search.json' ]
    }
    file_data = file.load_json(data_dict)
    assert isinstance(file_data, OrderedDict)
    assert file_data

    data_dict = {
        'path': 'config/routes/search.json'
    }
    file_data = file.load_json(data_dict)
    assert isinstance(file_data, OrderedDict)
    assert file_data

    # Test loading file where the first file isn't there
    data_dict = {
        'paths': [ 'invalid/test.json', 'config/routes/search.json' ]
    }
    file_data = file.load_json(data_dict)
    assert isinstance(file_data, OrderedDict)
    assert file_data

    data_dict = {
        'path': 'invalid/test.json',
        'paths': [ 'config/routes/search.json' ]
    }
    file_data = file.load_json(data_dict)
    assert isinstance(file_data, OrderedDict)
    assert file_data

    # Test loading an invalid file
    data_dict = {
        'paths': [ 'invalid/test.json' ]
    }
    file_data = file.load_json(data_dict)
    assert file_data is None

def test_create_json_response():
    # Test loading a json
    data_dict = {
        'paths': [ 'config/routes/search.json' ]
    }
    resp = file.create_json_response(data_dict)
    assert isinstance(resp, RequestsResponse)
    assert resp.status_code == 200

    # Test loading an invalid file
    data_dict = {
        'paths': [ 'invalid/test.json' ]
    }
    resp = file.create_json_response(data_dict)
    assert isinstance(resp, RequestsResponse)
    assert resp.status_code == 200
    assert not resp.content

def test_load_matched_json():
    # Test matching etd config file successfully
    data_dict = {
        'location': 'config/metadata_1',
        'view_args': {
            'namespace': 'etd'
        },
        'item': {
            'model_type': 'info:fedora/islandora:sp_pdf'
        }
    }
    with app.app_context():
        file_data = file.load_matched_json(data_dict)
        assert isinstance(file_data, dict)
        assert file_data
        assert 'test_filename' in file_data
        assert file_data['test_filename'] == "etd.json"

    # Test loading directory with invalid match conditions
    data_dict = {
        'location': 'config/metadata_2',
        'view_args': {
            'namespace': 'etd'
        },
        'item': {
            'model_type': 'info:fedora/islandora:sp_pdf'
        }
    }
    with app.app_context():
        file_data = file.load_matched_json(data_dict)
        assert not isinstance(file_data, dict)
        assert not file_data

    # Testing the on_fail functionality in load_matched_json when the config path is invalid
    data_dict['location'] = "metadata_config_invalid_path"
    data_dict['on_fail'] = 404
    with app.app_context():
        file_data = file.load_matched_json(data_dict)
        assert file_data is None    # expect None return, as base processor will throw the abort
