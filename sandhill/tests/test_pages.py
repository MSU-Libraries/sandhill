'''
Runs functional tests
'''
import os
import re
import pytest
import json
import hashlib
import collections
from sandhill.utils.config_loader import load_json_config
from sandhill import app

# Setup parameters for test_page
pages_conf = os.path.join(app.instance_path, "tests/pages.json")
pages = load_json_config(pages_conf)

@pytest.mark.functional
def test_pages_loadable():
    """
    Validate JSON can be parsed if present
    """
    if os.path.exists(pages_conf):
        loaded = json.load(open(pages_conf, 'r'), object_pairs_hook=collections.OrderedDict)
        assert isinstance(loaded, list)
        if len(loaded):
            assert isinstance(loaded[0], collections.OrderedDict)


@pytest.mark.functional
@pytest.mark.parametrize("page", pages)
def test_page(page):
    """
    Load the instance/tests/pages.json and perform
    functional tests on each entry within the file
    """

    with app.test_client() as client:
        app.logger.info(f"Functional page test context: {dict(page)}")
        resp = client.get(page['page'])
        assert resp.status_code == page['code']

        test_keys = page.keys()
        for test in test_keys:
            assert test in [
                '_comment', 'page', 'code', 'contains', 'excludes',
                'matches', 'md5'
            ]

        # Validate expected strings appear in response
        if 'contains' in page:
            for needle in page['contains']:
                assert needle in resp.data.decode("utf-8")

        # Validate expected strings do not appear in response
        if 'excludes' in page:
            for needle in page['excludes']:
                assert needle not in resp.data.decode("utf-8")

        # Validate matches against a regex string in the response
        if 'matches' in page:
            for needle in page['matches']:
                assert re.search(needle, resp.data.decode("utf-8"))

        # Validate response content matches given md5
        if 'md5' in page:
            hasher = hashlib.md5()
            hasher.update(resp.data)
            assert page['md5'] == hasher.hexdigest()
