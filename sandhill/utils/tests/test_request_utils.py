from sandhill import app
from pytest import raises
from sandhill.utils import request
from werkzeug.exceptions import HTTPException


def test_match_request_format():
    # Test standard search request using default format
    with app.test_request_context('/search?q=elephant'):
        result_format = request.match_request_format("format", ["text/html", "text/json"])
        assert result_format == "text/html"

    # Test standard search requesting json response with '.json'
    with app.test_request_context('/search.json?q=elephant'):
        result_format = request.match_request_format("format", ["text/html", "text/json"])
        assert result_format == "text/json"

    # Test standard search requesting json via Accept header
    with app.test_request_context('/search?q=elephant', headers=[("Accept", "text/json")]):
        result_format = request.match_request_format("format", ["text/html", "text/json"])
        assert result_format == "text/json"

    # Test passing in invalid format
    with app.test_request_context('/search.xml?q=elephant'):
        with raises(HTTPException) as http_error:
            result_format = request.match_request_format("format", ["text/html", "text/json"])
        assert http_error.type.code == 501


def test_overlay_with_query_args():
    # Test configs analagous to those in search_configs
    query_config = {
        "q": {
            "base": ["elephant"]
           },
        "rows":{
            "default": 20,
            "max": 100
        },
        "rows_min": {
            "default": 20,
            "min": 5
        },
        "start": {
            "default": 0
        },
        "fl": {
            "default": ["PID", "title"],
            "base": "PID"
        },
        "q.alt": {
            "default": ""
        }
    }
    # Testing that base values will override user-input params; max is implemented; default is overwritten; lists are combined as expected
    with app.test_request_context('/search?q=antelope&rows=120&rows_min=abc&start=5&fl=author&fl=date'):
        query_params = request.overlay_with_query_args(query_config)
        assert query_params["q"] == ['elephant']
        assert query_params["rows"] == ['100']
        assert query_params["start"] == ['5']
        assert "PID" in query_params["fl"]
        assert "author" in query_params["fl"]
        assert "date" in query_params["fl"]
        assert "title" not in query_params["fl"]
        assert query_params["rows_min"] == ["5"]

    # Testing that min is applied correctly; that defaults are used if not overwritten by user; that only unique values are returned;
    # that empty strings don't get included from configs; that user params not in configs are ignored.
    with app.test_request_context('/search?rows=1&rows_min=1&hello=world'):
        query_params = request.overlay_with_query_args(query_config)
        assert query_params["rows"] == ['1']
        assert query_params["rows_min"] == ['5']
        assert "PID" in query_params["fl"]
        assert "title" in query_params["fl"]
        assert len(query_params["fl"]) == 2
        assert "hello" not in query_params
        assert "q.alt" not in query_params
        assert query_params["q"] == ["elephant"]

