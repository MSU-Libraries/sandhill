import os
from sandhill import app
from sandhill.utils import config_loader
from pytest import raises
from collections import OrderedDict

def test_load_json_config():
    # test valid file path which has properly formatted json
    config_path = os.path.join(app.root_path, "test_instance/route_configs/home.json")
    data = config_loader.load_json_config(config_path)
    assert isinstance(data, dict)
    assert "route" in data

    # test an invalid file path
    data = config_loader.load_json_config("invalid")
    assert isinstance(data, dict)
    assert not data

    # test a malformatted json in a valid file path
    config_path = os.path.join(app.root_path, "test_instance/route_configs/invalid_format.json")
    data = config_loader.load_json_config(config_path)
    assert isinstance(data, dict)
    assert not data

def test_get_all_routes():
    app.instance_path = os.path.join(app.root_path, "test_instance/")

    # test valid route config path; the route in the config file is a list
    data = config_loader.get_all_routes()
    assert isinstance(data, list)
    assert '/home' in data

    # test valid route config path; the route in the config file is a string
    data = config_loader.get_all_routes()
    assert isinstance(data, list)
    assert '/about' in data

    # test valid path containing no route configs
    data = config_loader.get_all_routes("search_configs")
    assert isinstance(data, list)
    assert not data

    # test for an invalid route congfig path
    data = config_loader.get_all_routes("invalid_path")
    assert isinstance(data, list)
    assert not data

def test_load_route_config():
    app.instance_path = os.path.join(app.root_path, "test_instance/")

    # test a simple route config
    data = config_loader.load_route_config("/home")
    assert isinstance(data, dict)
    assert "route" in data

    # test route config that has only a string instead of list
    data = config_loader.load_route_config("/about")
    assert isinstance(data, dict)
    assert "route" in data

    # test for an invalid route congfig path
    data = config_loader.load_route_config("/invalid_path", "invalid_dir")
    assert isinstance(data, OrderedDict)
    assert not  data

def test_load_json_configs():
    # test providing a valid path
    config_path = os.path.join(app.root_path, "test_instance/route_configs")
    data = config_loader.load_json_configs(config_path)
    assert isinstance(data, dict)
    assert os.path.join(config_path, "home.json") in data

    # test providing an invalid path
    data = config_loader.load_json_configs("invalid_path")
    assert isinstance(data, dict)
    assert not data
   
    # test for a valid path without any json files
    config_path = os.path.join(app.root_path, "test_instance/txt_files")
    data = config_loader.load_json_configs(config_path)
    assert isinstance(data, dict)
    assert not data

    # test with the recurse flag
    config_path = os.path.join(app.root_path, "test_instance/")
    data = config_loader.load_json_configs(config_path, True)
    assert isinstance(data, dict)
    assert os.path.join(config_path, "route_configs", "home.json") in data

