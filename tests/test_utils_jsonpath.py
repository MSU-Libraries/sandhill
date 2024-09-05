import pytest
from jsonpath_ng.exceptions import JSONPathError
from sandhill.utils import jsonpath

def test_json_from_url():
    test_url_base = "https://jsonplaceholder.typicode.com"
    data = jsonpath.json_from_url(f"{test_url_base}/users")
    assert len(data) == 10
    assert data[0]['name'] == "Leanne Graham"

    data = jsonpath.json_from_url("Not-a-url")
    assert data is None

    data = jsonpath.json_from_url(f"{test_url_base}/invalid")
    assert data is None

    data = jsonpath.json_from_url(f"{test_url_base}/users", 0.000001)
    assert data is None

def test_find():
    data = {
        "key1": ["value1"],
        "key2": "value2",
        "key3": [
            {
                "subk1": "subv1",
                "subk2": "subv2",
            },
            {
                "subk1": "subv3",
                "subk2": "subv4",
            },
        ]
    }
    matches = jsonpath.find(data)
    assert matches == data
    matches = jsonpath.find(data, "$.key2")
    assert matches == ["value2"]
    matches = jsonpath.find(data, "$.key3[*].subk2")
    assert matches == ["subv2", "subv4"]
    matches = jsonpath.find(data, "path.not.found")
    assert len(matches) == 0
    with pytest.raises(JSONPathError):
        jsonpath.find(data, "invalid.$[*]-")
    matches = jsonpath.find(None, "$.id")
    assert len(matches) == 0
    # Validate deep copy
    subdata1 = data['key1']
    subdata2 = jsonpath.find(data, "$.key1")
    assert subdata1 is not subdata2[0]
    subdata2 = jsonpath.find(data, "$.key1", deepcopy=False)
    assert subdata1 is subdata2[0]

def test_set():
    data = {
        "key1": "value1",
        "key2": "value2",
        "key3": [
            {
                "subk1": "subv1",
                "subk2": "subv2",
            },
            {
                "subk1": "subv3",
                "subk2": "subv4",
            }
        ]
    }
    value = ["new", "value"]
    updated = jsonpath.put(data, "$.id", value)
    assert updated['id'] == value
    jsonpath.put(data, "$.key1", "UPDATED")
    assert data['key1'] == "value1"
    jsonpath.put(data, "$.key1", "UPDATED", deepcopy=False)
    assert data['key1'] == "UPDATED"
    with pytest.raises(ValueError):
        jsonpath.put(data, "$.key3[*]", "UPDATED")
    updated = jsonpath.put(data, "$.key3[1].subk1", "UPDATED")
    assert updated['key3'][1]['subk1'] == "UPDATED"

def test_append():
    data = {
        "key1": "value1",
        "key2": [3, 4, 5],
        "key3": [
            {
                "subk1": "subv1",
                "subk2": "subv2",
            },
            {
                "subk1": "subv3",
                "subk2": "subv4",
            }
        ]
    }
    updated = jsonpath.append(data, "key2", 6)
    assert updated['key2'] == [3, 4, 5, 6]
    assert data['key2'] == [3, 4, 5]
    with pytest.raises(ValueError):
        jsonpath.append(data, "key1", 1)
    jsonpath.append(data, "key3", { "subk1": "subv5" }, deepcopy=False)
    assert data['key3'][2]['subk1'] == 'subv5'

def test_delete():
    data = {
        "key1": "value1",
        "key2": [3, 4, 5],
        "key3": [
            {
                "subk1": "subv1",
                "subk2": "subv2",
            },
            {
                "subk1": "subv3",
                "subk2": "subv4",
            }
        ]
    }
    updated = jsonpath.delete(data, "$.key2[0]")
    assert updated['key2'] == [4, 5]
    updated = jsonpath.delete(data, "key3[1]")
    assert updated['key3'] == [{ "subk1": "subv1", "subk2": "subv2" }]
    updated = jsonpath.delete(updated, "key3[0].subk1")
    assert updated['key3'] == [{ "subk2": "subv2" }]
    jsonpath.delete(data, "$.key1")
    assert data["key1"] == "value1"
    jsonpath.delete(data, "$.key1", deepcopy=False)
    assert "key1" not in data
    with pytest.raises(ValueError):
        jsonpath.delete(data, "$.key2[*]")

def test_eval_within():
    ctx1 = {
        'item': { 'key1': 'val1' },
        'parent': { 'key2': 'val2' },
        'thing1': { 'key3': { 'a b': 'val3' } },
        'thing2': { 'key4': { 'key_5': 4 } },
        'thing3': { 'key6': [1, "two", 3.0] },
        'thing4': { 'key7': [2, 3, 4] }
    }
    string0 = "nothing_to == eval_here"
    assert jsonpath.eval_within(string0, ctx1) == "nothing_to == eval_here"

    string1 = "$.key1 == 'val1'"
    assert jsonpath.eval_within(string1, ctx1) == '"val1" == \'val1\''

    string2 = "$parent.key2 == \"val2\""
    assert jsonpath.eval_within(string2, ctx1) == '"val2" == "val2"'

    string3 = "$thing1.key3['a b'] == \"val3\""
    assert jsonpath.eval_within(string3, ctx1) == '"val3" == "val3"'

    string4 = "$thing2.key4.key_5 == 4"
    assert jsonpath.eval_within(string4, ctx1) == '4 == 4'

    string5 = "$thing3.key6 == [1, \"two\", 3.0]"
    assert jsonpath.eval_within(string5, ctx1) == '[1, \'two\', 3.0] == [1, "two", 3.0]'

    string6 = "$thing2.key4.key_5 == $thing4.key7[2]"
    assert jsonpath.eval_within(string6, ctx1) == '4 == 4'
    # No context given => nulop
    assert jsonpath.eval_within(string6, {}) == "$thing2.key4.key_5 == $thing4.key7[2]"

    string8 = "$thing1.wont.find.this == $missing.location[0]"
    assert jsonpath.eval_within(string8, ctx1) == "[] == []"
