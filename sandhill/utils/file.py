'''
Utility functions for files
'''
import itertools
import os
import zipfile

from urllib.parse import urlencode
from flask import request
from sandhill import app
from sandhill.utils.api import api_get

def download_file(
        url: str,
        filepath: str,
        passthrough_headers: list,
        retries : int = 0,
        api_get_function=api_get
) -> int|None:
    """
    Download a file at a given URL \n
    Args:
        url (str): The URL to download the file from.\n
        filepath (str): Full filepath where to download the file
        passthrough_headers (list): Headers to pass in the request \n
        retries (int): Number of retries to attempt \n
        api_get_function (function): function to use to make the download
    Returns:
        (int|None): Request code, None should never be returned \n
    Raises:
        (requests.RequestException): if the download request fails
    """
    return_code = None
    for loop in itertools.islice(itertools.count(), 0, retries + 1): # Number of retries wanted +1
        params = {'download': 'true'}
        app.logger.debug(f"Connecting to {url}?{urlencode(params)}")
        headers = {}
        for header in passthrough_headers:
            if header in request.headers:
                headers[header] = request.headers[header]
        # Stream the response to prevent loading the entire file into memory
        with api_get_function(url=url, params=params, headers=headers, stream=True) as r:
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: # filter out keep-alive chunks
                        f.write(chunk)
            if loop == retries:
                # Raises an HTTPError if the request returns a 4xx/5xx for the last attempts
                r.raise_for_status()
                return_code = r.status_code
    return return_code


def create_archive(zip_filepath: str, directory_to_zip: str, zip_inner_path: str = '/'):
    """
    Download a file at a given URL \n
    Args:
        zip_filepath (str): Full filepath of the created zip file.\n
        directory_to_zip (str): Filepath of the directory to compress
        zip_inner_path (str): Filepath within the archive where to add files \n
    Raises:
        (OSError): Generic OS error (e.g. file errors, permissions issues, locked file, invalid
            path, etc.).
        (RuntimeError): if compression type is unsupported or misconfigured; or writing after the
            archive is finalized.
        (ValueError): if invalid arguments (e.g., bad compression mode)
        (zipfile.LargeZipFile): if file size > 2 GiB and ZIP64 is not enabled.
        (zipfile.BadZipFile): if internal corruption occurs during writing (rare).
    """
    # TODO might be good at some point to have flags not to compress some file types
    #  (+ bonus for a config file)
    with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as archive:
        for root, _, files in os.walk(directory_to_zip):
            for file in files:
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, start=directory_to_zip)
                zip_inner_filepath = os.path.join(zip_inner_path, relative_path).replace("\\", "/")
                archive.write(filepath, zip_inner_filepath)
