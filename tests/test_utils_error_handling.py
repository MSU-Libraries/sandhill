from sandhill import app
from sandhill.utils import error_handling
from pytest import raises
from werkzeug.exceptions import HTTPException

def test_catch():

    @error_handling.catch(ValueError, "VALUE ERROR: {exc}", return_val=-1)
    @error_handling.catch((AttributeError, TypeError), "INVALID TYPE ERROR: {exc}", abort=400)
    @error_handling.catch(KeyError, return_arg="a")
    @error_handling.catch(IndexError, return_arg="add", return_val=None)
    @error_handling.catch(NameError, return_arg="invalid", return_val=2)
    @error_handling.catch(OSError, "OSError: Logging and reraising {exc}")
    def myfunc(a, **kwargs):
        if "extra" in kwargs:
            return 100
        if not isinstance(a, int):
            raise AttributeError("Only accepts int values")
        if a < 0:
            raise ValueError("Negatives are a no no!")
        if a == 1:
            raise KeyError("1 is not a valid key")
        if a == 10:
            raise IndexError("2 is not a valid index")
        if a == 20:
            raise NameError("this is a name error")
        if a == 30:
            raise OSError("Got me an OS here")
        return a * a

    ## Test no exceptions being raised
    res = myfunc(2)
    assert res == 4

    ## Test with kwargs
    res = myfunc(3, extra=4)
    assert res == 100

    ## Test for AttributeError
    ## Where an abort code is provided
    with raises(HTTPException) as http_error:
        res = myfunc("four")
    assert http_error.type.code == 400

    # Test for ValueError
    # Where a return_val is provided
    res = myfunc(-3)
    assert res == -1

    # Test when no message is provided
    res = myfunc(1)
    assert res == 1

    # Test when return_kwarg and return_val are provided
    res = myfunc(10, add=12)
    assert res == 12

    # Test when passing an invalid return_kwarg
    res = myfunc(20)
    assert res == 2

    # Test for not providing any action or return
    with raises(OSError):
        res = myfunc(30)
