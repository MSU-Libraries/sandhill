import os
from sandhill import app
from sandhill.utils import config_loader
from pytest import raises

def test_load_json_config():
    # TODO -- needs group review

    config_path = os.path.join(app.root_path, "test_instance/route_configs/home.json")
    data = config_loader.load_json_config(config_path)
    assert isinstance(data, dict)
    assert "route" in data

    data = config_loader.load_json_config("invalid")
    assert isinstance(data, dict)
    assert not data

def test_get_all_routes():
    # TODO -- needs group review

    app.instance_path = os.path.join(app.root_path, "test_instance/")

    # test valid route config path
    data = config_loader.get_all_routes()
    assert isinstance(data, list)
    assert '/home' in data

    # test invalid route config path
    with raises(FileNotFoundError):
        data = config_loader.get_all_routes("invalid_path")

    # test valid path containing no route configs
    data = config_loader.get_all_routes("search_configs")
    assert isinstance(data, list)
    assert not data

def test_load_route_config():
    # TODO -- needs group review

    app.instance_path = os.path.join(app.root_path, "test_instance/")

    # test a simple route config
    data = config_loader.load_route_config("/home")
    assert isinstance(data, dict)
    assert "route" in data

    # test route config that has only a string instead of list
    data = config_loader.load_route_config("/about")
    assert isinstance(data, dict)
    assert "route" in data

def test_load_json_configs():
    # TODO -- needs group review

    # test providing a valid path
    config_path = os.path.join(app.root_path, "test_instance/route_configs")
    data = config_loader.load_json_configs(config_path)
    assert isinstance(data, dict)
    assert os.path.join(config_path, "home.json") in data

    # test providing an invalid path
    data = config_loader.load_json_configs("invalid_path")
    assert isinstance(data, dict)
    assert not data
