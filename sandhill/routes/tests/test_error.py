'''
Test the error.py file
'''
from werkzeug.exceptions import HTTPException, NotFound
from sandhill.routes import error
from sandhill import app

def test_handle_http_abort():
    '''
    Test the handle_http_abort function
    '''

    # Test an exception with a accpet header of json
    with app.test_request_context("/", headers={'Accept':'application/json'}):
        resp, code = error.handle_http_abort(NotFound())
        assert resp.headers['Content-Type'] == 'application/json'
        assert resp.get_json()['code'] == 404
        assert code == 404

    # Test an exception with no extra headers passed
    with app.test_request_context("/"):
        resp, code = error.handle_http_abort(NotFound())
        assert isinstance(resp, str)
        assert code == 404
        assert "404 Not Found" in resp

