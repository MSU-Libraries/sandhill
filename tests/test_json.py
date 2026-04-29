'''
Test the JSON syntax of all files in the instance directory
'''

import os
import json
import pytest
from sandhill import app

def get_search_dir():
    """
    Get the directory to search for JSON files.
    Returns None if the instance path is within a tests directory.
    """
    # Ignore the tests directory since that has invalid JSON for testing purposes
    if "/tests/" in app.instance_path:
        return None
    return app.instance_path

def get_instance_json_files():
    """
    Get a list of all JSON files in the instance directory.
    """
    search_dir = get_search_dir()
    if not search_dir or not os.path.exists(search_dir):
        return []

    json_files = []
    for root, dirs, files in os.walk(search_dir):
        for f in files:
            if f.endswith(".json"):
                json_files.append(os.path.join(root, f))
    return json_files

def test_json_syntax():
    """
    Validate JSON syntax for all JSON files in the instance directory
    """
    search_dir = get_search_dir()
    if search_dir is None:
        pytest.skip("Skipping JSON validation for test instance directory")

    json_files = get_instance_json_files()

    # Ensure there is at least something to test if we aren't in a test environment
    assert len(json_files) > 0, f"No JSON files found in instance directory: {search_dir}"

    for fpath in json_files:
        with open(fpath, 'r') as json_file:
            try:
                json.load(json_file)
            except json.JSONDecodeError as exc:
                pytest.fail(f"Invalid JSON syntax in {fpath}: {exc}")
