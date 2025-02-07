import os
from copy import deepcopy
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

def test_getindex():
    assert generic.getindex(['a','b'], 1) == 'b'
    assert generic.getindex(['a','b'], '1') == 'b'
    assert generic.getindex(['a','b'], 'x', 1) == 'b'
    assert generic.getindex(['a','b'], 'x', 3) is None
    assert generic.getindex(['a','b'], 'x', 3, 'y') == 'y'

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
    assert 'SECRET_KEY' not in os.environ

    # Test getting a value from when it is set in the environment and config
    response = generic.getconfig("PYTHON_SHA256")
    assert response == "FAKE_SHA"

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

def test_pop_dict_matching_key():
    haystack = [
        {'key1': 10, 'hay1': 'a'},
        {'key2': 20, 'hay2': 'b'},
    ]
    match_none = {'key0': 0, 'match0': '.'}
    match_no = {'key1': 99, 'match1': 'y'}
    match_one = {'key1': 10, 'match1': 'x'}
    match_two = {'key2': 20, 'match1': 'z'}

    assert generic.pop_dict_matching_key(haystack, match_none, 'key0') == []
    assert generic.pop_dict_matching_key(haystack, match_no, 'key1') == []
    assert generic.pop_dict_matching_key(haystack.copy(), match_one, 'key1') == [haystack[0]]
    assert generic.pop_dict_matching_key(haystack.copy(), match_two, 'key2') == [haystack[1]]

def test_overlay_dicts_matching_key():
    target = [
        {'key1': 10, 'tgt1': 'a'},
        {'key1': 20, 'tgt2': 'b'},
        {'key2': 30, 'tgt3': 'c'},
    ]
    match_none = {'key0': 0, 'match0': '.'}
    match_no = {'key1': 99, 'match1': 'y'}
    match_one = {'key1': 10, 'match1': 'x'}
    match_again = {'key1': 10, 'match1': 'xx'}
    match_two = {'key1': 20, 'match1': 'z'}

    tcopy = deepcopy(target)
    generic.overlay_dicts_matching_key(tcopy, [match_none], 'key0')
    assert tcopy == target + [match_none]

    tcopy = deepcopy(target)
    generic.overlay_dicts_matching_key(tcopy, [match_no], 'key1')
    assert tcopy == target + [match_no]

    tcopy = deepcopy(target)
    generic.overlay_dicts_matching_key(tcopy, [match_one], 'key1')
    assert tcopy == [target[1], target[2], {**target[0], **match_one}]

    tcopy = deepcopy(target)
    generic.overlay_dicts_matching_key(tcopy, [match_one, match_again, match_two], 'key1')
    assert tcopy == [target[2], {**target[0], **match_one}, {**target[0], **match_again}, {**target[1], **match_two}]

def test_recursive_merge():
    dict1 = {
        'key1': 10,
        'key2': 'a',
        'key3': {
            'sub_key': 'lalala'
        },
        'key4': {
            'sub_key': 'lololo'
        },
        'key5': 'a',
    }
    dict2 = {
        'key2': 20,
        'key3': 'b',
        'key4': {
            'sub_key2': 'lilili'
        },
        'key5': None,
    }
    dict3 = {
        'key1': 10,
        'key2': 20,
        'key3': 'b',
        'key4': {
            'sub_key': 'lololo',
            'sub_key2': 'lilili',
        },
    }

    assert dict3 == generic.recursive_merge(dict1, dict2)
    assert dict3 == generic.recursive_merge(dict3, {})
    with raises(RecursionError):
        generic.recursive_merge(dict1, dict2, 1)
    with raises(TypeError):
        generic.recursive_merge(dict3, None)
    with raises(TypeError):
        generic.recursive_merge(None, {})
    with raises(TypeError):
        generic.recursive_merge(1, {})
    with raises(TypeError):
        generic.recursive_merge({}, {}, 'aa')
