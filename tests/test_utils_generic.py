import os
from pytest import raises
from sandhill.utils import generic
from sandhill import app

def test_ifnone():
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

def test_tolist():
    # Test if the result is a list
    assert generic.tolist("test_string") == ["test_string"]
    assert generic.tolist("test_string1", "test_string2") == ["test_string1", "test_string2"]
    assert generic.tolist(["test_string"], "test_string1", "test_string2") == ["test_string", "test_string1", "test_string2"]
    assert generic.tolist(["test_string"], ["test_string1", "test_string2"]) == ["test_string", "test_string1", "test_string2"]
    assert generic.tolist(["test_string"], {"key":"value"}) == ["test_string", {"key":"value"}]
    assert generic.tolist() == []

def test_touniquelist():
    # Test if the result is a list with unique items
    assert generic.touniquelist("test_string") == ["test_string"]
    assert generic.touniquelist("test_string1", "test_string2") == ["test_string1", "test_string2"]
    assert generic.touniquelist(["test_string"], "test_string", "test_string2") == ["test_string", "test_string2"]
    assert generic.touniquelist(["test_string"], {"key":"value"}, {"key":"value"}) == ["test_string", {"key":"value"}]
    assert generic.touniquelist() == []

def test_getdescendant():
    # Test if the correct level in the dict is returned
    test_dict= {
            "level1": {
                "level2": {
                    "level3":{
                        "level4": "val"
                    }
                }
            },
            "other_level": "other_val",
            "dict1": [
                "list2",
                {
                    "dict3": [97,98,99]
                }
            ]
        }
    assert generic.getdescendant(test_dict, []) is None
    assert generic.getdescendant(test_dict, ['level1', 'level2']) == test_dict['level1']['level2']
    assert generic.getdescendant(test_dict, ['level1', 'level2', 'level3', 'level4']) == "val"
    assert generic.getdescendant(test_dict, ['other_level']) == test_dict['other_level']
    assert generic.getdescendant(test_dict, ['level1', 'invalid_level']) is None
    assert generic.getdescendant(test_dict, ['dict1', "0"]) == "list2"
    assert generic.getdescendant(test_dict, ['dict1', 1, 'dict3', 2]) == 99
    assert generic.getdescendant('invalid_dict', ['level1', 'invalid_level']) is None

    assert generic.getdescendant(test_dict, "dict1.1.dict3.0") == 97
    pull = generic.getdescendant(test_dict, "dict1.1.dict3.0", extract=True)
    assert pull == 97
    assert generic.getdescendant(test_dict, "dict1.1.dict3") == [98,99]
    generic.getdescendant(test_dict, "dict1.1.dict3", put=[1,2,3])
    assert generic.getdescendant(test_dict, "dict1.1.dict3.2") == 3
    generic.getdescendant(test_dict, "dict1.1.newkey", put="new!")
    assert generic.getdescendant(test_dict, "dict1.1.newkey") == "new!"
    generic.getdescendant(test_dict, "dict1.[]", put="33")
    assert generic.getdescendant(test_dict, "dict1.2") == "33"
    generic.getdescendant(test_dict, "dict1.2", put=42)
    assert generic.getdescendant(test_dict, "dict1.2") == 42

    with raises(IndexError):
        generic.getdescendant(test_dict, "dict1.strkey", put="using str as index for list")

def test_getconfig():
    # Test getting a value from the environment when also present in config
    response = generic.getconfig("PATH")
    assert isinstance(response, str)
    assert response

    # Test getting a value from the config when it is not set in the environment
    response = generic.getconfig("SECRET_KEY")
    assert response == app.config["SECRET_KEY"]

    # Test getting a value from the config when it is set in the environment
    response = generic.getconfig("DEBUG")
    assert response == os.environ["DEBUG"] if "DEBUG" in os.environ else "0"

    # Test getting a value for a config not set in the environment or config
    response = generic.getconfig("NOT_SET")
    assert response is None

    # Test getting a value for a config that is empty in the config
    response = generic.getconfig("TEST_EMPTY")
    assert isinstance(response, str)
    assert not response

def test_getmodulepath():
    install_path = os.path.dirname(app.root_path)
    assert generic.getmodulepath(install_path + '/sandhill/') == 'sandhill'
    assert generic.getmodulepath(install_path + '/instance/') == 'instance'
    assert generic.getmodulepath(install_path + '/tests/instance/') == 'tests.instance'
    assert generic.getmodulepath(install_path + '/sandhill/utils/filters') == 'sandhill.utils.filters'
    assert generic.getmodulepath(install_path + '/sandhill/utils/filters.py') == 'sandhill.utils.filters'
    assert generic.getmodulepath(install_path + '/invalid/subpath') == 'invalid.subpath'
    assert generic.getmodulepath('/completely/invalid/path') == 'completely.invalid.path'
