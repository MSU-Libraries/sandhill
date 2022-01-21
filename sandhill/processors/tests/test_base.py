import os
from collections import OrderedDict
from flask import request
from pytest import raises
from werkzeug.exceptions import HTTPException
from sandhill.processors import base
from sandhill import app
from sandhill.utils.context import list_custom_context_processors
from sandhill.bootstrap import requests

def test_load_route_data():
    route_data = [
         OrderedDict({
            "processor": "file.load_json",
            "name": "search_conf",
            "on_fail": 501,
            "paths": [
                "config/search/main.json"
            ]
        }),
        OrderedDict({
            "processor": "request.get_url_components",
            "name": "url_components",
            "on_fail": 500
        }),
        OrderedDict({
            "processor": "template.render_string",
            "name": "string1",
            "value": "A MISING STRING",
            "when": "{{ 1 == 0 }}"
        }),
        OrderedDict({
            "processor": "template.render_string",
            "name": "string2",
            "value": "A REAL STRING",
            "when": "{{ 1 == 1 }}"
        })
    ]

    # Test positive route data load
    with app.test_request_context('/etd/1000'):
        app.preprocess_request()
        loaded = base.load_route_data(route_data)
        assert isinstance(loaded, dict)
        assert loaded

        # Validate when conditions
        assert 'string1' not in loaded
        assert 'string2' in loaded
        assert loaded['string2'] == "A REAL STRING"

    # Test of the on fail error code is valid
    route_data = [
        OrderedDict({
            "processor": "request.invalid_action",
            "name": "url_components",
            "on_fail": 7000
        })
    ]
    with app.test_request_context('/etd/1000'):
        with raises(LookupError) as lookup_error:
            loaded = base.load_route_data(route_data)
        assert "no exception for" in str(lookup_error.value)

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
        for ctxp in list_custom_context_processors():
            del loaded[ctxp]
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
        for ctxp in list_custom_context_processors():
            del loaded[ctxp]
        assert not loaded

    # Test invalid when condition
    route_data = [
         OrderedDict({
            "processor": "template.render_string",
            "name": "string",
            "value": "dummy",
            "when": "NOT A TYPE"
        })
    ]
    with app.test_request_context('/etd/1000'):
        with raises(HTTPException) as http_error:
            loaded = base.load_route_data(route_data)
        assert 500 == http_error.type.code

    # Test invalid char in request, causing a JSON decode failure
    route_data = [
         OrderedDict({
            "processor": "template.render_string",
            "name": "string",
            "value": "{{ view_args.namespace }}",
        })
    ]
    with app.test_request_context('/dummy'):
        request.view_args = { 'namespace': "a\\.aspx" }
        with raises(HTTPException) as http_error:
            loaded = base.load_route_data(route_data)
        assert 400 == http_error.type.code
