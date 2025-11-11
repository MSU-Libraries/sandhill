'''
Test the file utility
'''
import tempfile
import os
import shutil

from sandhill import app
from sandhill.bootstrap import sandbug
from sandhill.utils.file import download_file, create_archive
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
        # create_archive(zip_filepath: str, directory_to_zip: str, zip_inner_path: str = '/'):
        file.write(b'Test text')
        destination_path = os.path.join(d, os.path.basename(file.name))
        shutil.move(file.name, destination_path)

        create_archive(zip.name, d)

        assert os.path.getsize(zip.name) > 0
        # TODO test if the archive exists and not empty
