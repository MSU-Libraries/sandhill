from sandhill.utils import filters

def test_islist():
    assert filters.is_list([]) == True
    assert filters.is_list(['a',1]) == True
    assert filters.is_list({'a':1}) == False
    assert filters.is_list("string") == False
    assert filters.is_list(None) == False
