import os
from collections import OrderedDict
from pytest import raises
from werkzeug.exceptions import HTTPException
from sandhill.processors import base
from sandhill import app

def test_load_route_data():
    app.instance_path = os.path.join(app.root_path, "test_instance/")

    route_data = [
         OrderedDict({
            "processor": "file.load_json",
            "name": "search_conf",
            "on_fail": 501,
            "paths": [
                "search_configs/main.json"
            ]
        }),
        OrderedDict({
            "processor": "request.get_url_components",
            "name": "url_components",
            "on_fail": 500
        })
    ]

    # Test positive route data load
    with app.test_request_context('/etd/1000'):
        loaded = base.load_route_data(route_data)
        assert isinstance(loaded, dict)
        assert loaded

    # Test invalid on_fail
    route_data = [
         OrderedDict({
            "processor": "file.invalid_teapot",
            "name": "invalid",
            "on_fail": "teapot"
        })
    ]
    with app.test_request_context('/etd/1000'):
        with raises(HTTPException) as http_error:
            loaded = base.load_route_data(route_data)
        assert 500 == http_error.type.code

    # Test loading invalid processors
    route_data = [
         OrderedDict({
            "processor": "fake.invalid",
            "name": "invalid"
        })
    ]
    with app.test_request_context('/etd/1000'):
        loaded = base.load_route_data(route_data)
        assert isinstance(loaded, dict)
        del loaded['view_args']
        assert not loaded

    # Test invalid function on valid processor with valid on_fail set
    route_data = [
         OrderedDict({
            "processor": "file.invalid_teapot",
            "name": "invalid",
            "on_fail": 418
        })
    ]
    with app.test_request_context('/etd/1000'):
        with raises(HTTPException) as http_error:
            loaded = base.load_route_data(route_data)
        assert 418 == http_error.type.code

    # Test badly formed route (invalid keys)
    route_data = [
         OrderedDict({
            "processor": "file-invalid_teapot",
            "name": "invalid"
        })
    ]
    with app.test_request_context('/etd/1000'):
        loaded = base.load_route_data(route_data)
        assert isinstance(loaded, dict)
        del loaded['view_args']
        assert not loaded
