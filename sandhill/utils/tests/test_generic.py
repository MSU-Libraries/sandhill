import os
from pytest import raises
from sandhill.utils import generic
from sandhill import app

def test_is_none():
    # Test dictionary path
    assert generic.ifnone(None, "key", "default") == "default"
    assert generic.ifnone("non-dict", "key", "default") == "default"
    assert generic.ifnone(1, "key", "default") == "default"
    assert generic.ifnone({"a": 1}, "a", "default") == 1
    assert generic.ifnone({"a": 1}, "key", "default") == "default"

    # Test variable path
    assert generic.ifnone(None, "default") == "default"
    assert generic.ifnone("val", "default") == "val"
    assert generic.ifnone(1, "default") == 1

    # Test incorrect number of arguments
    with raises(TypeError) as type_error:
        result = generic.ifnone()

    with raises(TypeError) as type_error:
        result = generic.ifnone(1)

    with raises(TypeError) as type_error:
        result = generic.ifnone(1, 2, 3, 4)

def test_combine_to_list():
    # Test if the result is a list
    assert generic.combine_to_list("test_string") == ["test_string"]
    assert generic.combine_to_list("test_string1", "test_string2") == ["test_string1", "test_string2"]
    assert generic.combine_to_list(["test_string"], "test_string1", "test_string2") == ["test_string", "test_string1", "test_string2"]
    assert generic.combine_to_list(["test_string"], ["test_string1", "test_string2"]) == ["test_string", "test_string1", "test_string2"]
    assert generic.combine_to_list(["test_string"], {"key":"value"}) == ["test_string", {"key":"value"}]
    assert generic.combine_to_list() == []

def test_combine_to_unique_list():
    # Test if the result is a list with unique items
    assert generic.combine_to_unique_list("test_string") == ["test_string"]
    assert generic.combine_to_unique_list("test_string1", "test_string2") == ["test_string1", "test_string2"]
    assert generic.combine_to_unique_list(["test_string"], "test_string", "test_string2") == ["test_string", "test_string2"]
    assert generic.combine_to_unique_list(["test_string"], {"key":"value"}, {"key":"value"}) == ["test_string", {"key":"value"}]
    assert generic.combine_to_unique_list() == []

def test_get_descendant_from_dict():
    # Test if the correct level in the dict is returned
    test_dict= {
            "level1": {
                "level2": {
                    "level3":{
                        "level4": "val"
                        }
                    }
                },
            "other_level": "other_val"
        }
    assert generic.get_descendant_from_dict(test_dict, []) is None
    assert generic.get_descendant_from_dict(test_dict, ['level1', 'level2']) == test_dict['level1']['level2']
    assert generic.get_descendant_from_dict(test_dict, ['level1', 'level2', 'level3', 'level4']) == "val"
    assert generic.get_descendant_from_dict(test_dict, ['other_level']) == test_dict['other_level']
    assert generic.get_descendant_from_dict(test_dict, ['level1', 'invalid_level']) is None
    assert generic.get_descendant_from_dict('invalid_dict', ['level1', 'invalid_level']) is None

def test_get_config():
    # Test getting a value from the environment when also present in config
    response = generic.get_config("PATH")
    assert isinstance(response, str)
    assert response

    # Test getting a value from the config when it is not set in the environment
    response = generic.get_config("SECRET_KEY")
    assert response == app.config["SECRET_KEY"]

    # Test getting a value from the config when it is set in the environment
    response = generic.get_config("DEBUG")
    assert response == os.environ["DEBUG"] if "DEBUG" in os.environ else "0"

    # Test getting a value for a config not set in the environment or config
    response = generic.get_config("NOT_SET")
    assert response is None

    # Test getting a value for a config that is empty in the config
    response = generic.get_config("TEST_EMPTY")
    assert isinstance(response, str)
    assert not response

def test_get_module_path():
    install_path = os.path.dirname(app.root_path)
    assert generic.get_module_path(install_path + '/sandhill/') == 'sandhill'
    assert generic.get_module_path(install_path + '/instance/') == 'instance'
    assert generic.get_module_path(install_path + '/sandhill/test_instance/') == 'sandhill.test_instance'
    assert generic.get_module_path(install_path + '/sandhill/utils/filters') == 'sandhill.utils.filters'
    assert generic.get_module_path(install_path + '/sandhill/utils/filters.py') == 'sandhill.utils.filters'
    assert generic.get_module_path(install_path + '/invalid/subpath') == 'invalid.subpath'
    assert generic.get_module_path('/completely/invalid/path') == 'completely.invalid.path'
