'''
Test the static.py file
'''
from sandhill import app


def test_handle_static():
    '''
    tests the handle_static function
    '''
    client = app.test_client()

    # test getting a file from instance directory
    result = client.get("/static/test.txt")
    assert result.status_code == 200

    # test getting a file from sandhill static directory
    result = client.get("/static/favicon.ico")
    assert result.status_code == 200

    # test an invalid file
    result = client.get("/static/not-a-file")
    assert result.status_code == 404

def test_favicon():
    '''
    tests the favicon function
    '''
    # test retrieving the favicon.ico file
    client = app.test_client()
    result = client.get("/favicon.ico")
    assert result.status_code == 200
