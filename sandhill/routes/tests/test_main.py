'''
Tests the main.py route file
'''
from sandhill import app

def test_main():
    '''
    Tests the main function
    '''
    with app.test_client() as client:
        # test loading a page that has no data to load
        result = client.get('/')
        assert result.status_code == 200

        # test loading a page that does have data to load
        result = client.get('/about')
        assert result.status_code == 200

        # test streaming a page
        result = client.get('/stream')
        assert result.status_code == 200

        # test an invalid page
        result = client.get('/invalid/page/route')
        assert result.status_code == 404

        # test route with invalid data specification
        result = client.get('/invalid-data')
        assert result.status_code == 200

        # test an invalid route config
        result = client.get('/missing')
        assert result.status_code == 500

        # test whether jsonify(data) is returned when app.debug is true
        old_debug = app.debug
        app.debug = True
        result = client.get('/missing')
        assert result.status_code == 200
        assert result.headers["Content-Type"] == "application/json"
        app.debug = old_debug   # restore debug setting

        # test passing in a route config that contains no data
        result = client.get('/no-data')
        assert result.status_code == 200
