from pytest import raises
from sandhill.utils import generic

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
