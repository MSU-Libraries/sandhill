from sandhill import app
from sandhill.utils import decorators
from pytest import raises
from werkzeug.exceptions import HTTPException

def test_catch():

    @decorators.catch(ValueError, "VALUE ERROR: {exc}", return_val=-1)
    @decorators.catch((AttributeError, TypeError), "INVALID TYPE ERROR: {exc}", abort=400)
    @decorators.catch(ZeroDivisionError, "ZERO DIVISION ERROR: {exc}")
    def myfunc(a, **kwargs):
        print(f"myfunc kwargs: {kwargs}")
        if "extra" in kwargs:
            return 100
        if not isinstance(a, int):
            raise AttributeError("Only accepts int values")
        if a < 0:
            raise ValueError("Negatives are a no no!")
        if a == 0:
            raise ZeroDivisionError("Zero is not allowed")
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

    # Test for ZeroDivisionError
    # Where no return_val or abort_code is provided
    with raises(HTTPException) as http_error:
        res = myfunc(0)
    assert http_error.type.code == 500
