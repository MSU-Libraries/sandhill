'''
Test the static.py file
'''
from sandhill import app


def test_handle_static():
    '''
    tests the handle_static function
    '''
    with app.test_client() as client:
        # test getting a file from instance directory
        result = client.get("/static/test.txt")
        assert result.status_code == 200
        result.close()

        # test getting a file from sandhill static directory
        result = client.get("/static/favicon.ico")
        assert result.status_code == 200
        result.close()

        # test an invalid file
        result = client.get("/static/not-a-file")
        assert result.status_code == 404
        result.close()

def test_favicon():
    '''
    tests the favicon function
    '''
    with app.test_client() as client:
        # test retrieving the favicon.ico file
        result = client.get("/favicon.ico")
        assert result.status_code == 200
        result.close()
