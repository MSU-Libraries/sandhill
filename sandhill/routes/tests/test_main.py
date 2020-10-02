import os
from sandhill import app


def test_main():
    client = app.test_client()

    # test loading a page that has no data to load
    result = client.get('/')
    assert result.status_code == 200

    # test loading a page that does have data to load
    result = client.get('/about')
    assert result.status_code == 200

    # test streaming a page

    # test an invalid page
    result = client.get('/invalid/page/route')
    assert result.status_code == 404

def test_handle_template():
    pass # TODO

def test_handle_stream():
    pass # TODO
