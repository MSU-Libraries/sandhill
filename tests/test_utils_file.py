'''
Test the file utility
'''
import tempfile
import os
import shutil

from sandhill import app
from sandhill.bootstrap import sandbug
from sandhill.utils.file import download_file, create_archive, write_json_data
from sandhill.utils.jsonpath import delete
from sandhill.utils.test import _test_api_get_json, _test_api_get_json_error, _test_api_get_redirect
from requests.exceptions import HTTPError
from pytest import raises

def test_download_file():
    with tempfile.NamedTemporaryFile() as f, app.test_request_context('/etd/1000', headers=[("Range", "0-100")]):
        filename = f.name
        #  Download happens correctly
        assert download_file('http://dummy_URL', filename, ['Range'], 0, _test_api_get_json) == 200

        # Download fails with a 400
        with raises(HTTPError) as err:
            download_file('http://dummy_URL', filename, [], 0, _test_api_get_json_error)
        # assert err.response.status_code == 400 # TODO should be nice to implement checking the response code

        # Download gets a 300
        assert download_file('http://dummy_URL', filename, [], 0, _test_api_get_redirect) == 300
    # TODO test the retry

def test_create_archive():
    with tempfile.TemporaryDirectory() as d, tempfile.NamedTemporaryFile() as zip, tempfile.NamedTemporaryFile() as file:
        file.write(b'Test text')
        destination_path = os.path.join(d, os.path.basename(file.name))
        shutil.move(file.name, destination_path)
        callback_called = {'called': False}
        def callback_function(filename, size):
            callback_called['called'] = True

        create_archive(zip.name, d, update_function=callback_function)

        assert os.path.getsize(zip.name) > 0
        assert callback_called['called'] == True
        # TODO test if the archive exists and not empty

def test_write_json_data():
    with tempfile.NamedTemporaryFile() as file:
        write_json_data(file.name, {'data':123})
        assert os.path.getsize(file.name) > 0
