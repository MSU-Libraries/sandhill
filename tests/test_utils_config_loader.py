import os
from sandhill import app
from sandhill.utils import config_loader
from sandhill.modules.routing import Route
from pytest import raises
from collections import OrderedDict

def test_load_json_config():
    # test valid file path which has properly formatted json
    config_path = os.path.join(app.instance_path, "config/routes/home.json")
    data = config_loader.load_json_config(config_path)
    assert isinstance(data, dict)
    assert "routes" in data

    # test an invalid file path
    data = config_loader.load_json_config("invalid")
    assert isinstance(data, dict)
    assert not data

    # test a malformatted json in a valid file path
    config_path = os.path.join(app.instance_path, "config/routes/invalid_format.json")
    data = config_loader.load_json_config(config_path)
    assert isinstance(data, dict)
    assert not data

def test_get_all_routes():
    # test valid route config path; the route in the config file is a list
    data = config_loader.get_all_routes()
    assert isinstance(data, list)
    assert any(['/home' in route.rule for route in data])

    # test valid route config path; the route in the config file is a string
    data = config_loader.get_all_routes()
    assert isinstance(data, list)
    assert any(['/about' in route.rule for route in data])

    # test valid path containing no route configs
    data = config_loader.get_all_routes("config/search/")
    assert isinstance(data, list)
    assert data == [Route('/')]

    # test for an invalid route congfig path
    data = config_loader.get_all_routes("invalid_path")
    assert isinstance(data, list)
    assert data == [Route('/')]

    # test load sorting for routes
    data = config_loader.get_all_routes()
    rules = [route.rule for route in data]
    assert rules.index('/alpha/<string:value>') < rules.index('/<string:value>/alpha')
    assert rules.index('/beta/<string:value>') < rules.index('/<string:value>/beta')
    assert rules.index('/beta') < rules.index('/<string:value>/beta')
    assert rules.index('/beta') < rules.index('/<string:value>')
    assert rules.index('/alpha/<string:value>/beta') < rules.index('/alpha/<string:value>')

def test_load_route_config():
    # test a simple route config
    data = config_loader.load_route_config("/home")
    assert isinstance(data, dict)
    assert "routes" in data

    # test route config that has only a string instead of list
    data = config_loader.load_route_config("/about")
    assert isinstance(data, dict)
    assert "route" in data

    # test for an invalid route congfig path
    data = config_loader.load_route_config("/invalid_path", "invalid_dir")
    assert isinstance(data, OrderedDict)
    assert data == OrderedDict([('route', ['/']), ('template', 'home.html.j2')])

def test_load_json_configs():
    # test providing a valid path
    config_path = os.path.join(app.instance_path, "config/routes/")
    data = config_loader.load_json_configs(config_path)
    assert isinstance(data, dict)
    assert os.path.join(config_path, "home.json") in data

    # test providing an invalid path
    data = config_loader.load_json_configs("invalid_path")
    assert isinstance(data, dict)
    assert not data
   
    # test for a valid path without any json files
    config_path = os.path.join(app.instance_path, "txt_files")
    data = config_loader.load_json_configs(config_path)
    assert isinstance(data, dict)
    assert not data

    # test with the recurse flag
    config_path = app.instance_path
    data = config_loader.load_json_configs(config_path, True)
    assert isinstance(data, dict)
    assert os.path.join(config_path, "config/routes/", "home.json") in data

