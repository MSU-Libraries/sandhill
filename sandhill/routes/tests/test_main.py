'''
Tests the main.py route file
'''
import io
from flask import Response as FlaskResponse
from werkzeug.exceptions import HTTPException
from requests.models import Response as RequestsResponse
from pytest import raises
from sandhill import app
from sandhill.routes import main


def test_main():
    '''
    Tests the main function
    '''
    client = app.test_client()

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
    assert result.status_code == 404
