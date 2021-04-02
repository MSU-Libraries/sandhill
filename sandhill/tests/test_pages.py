'''
Runs functional tests
'''
import os
import pytest
from sandhill.utils.config_loader import load_json_config
from sandhill import app

# TODO added checks around these lines
pages_conf = os.path.join(app.instance_path, "tests/pages.json")
pages = load_json_config(pages_conf)

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

        # Validate expected strings appear in response
        if 'contains' in page:
            for needle in page['contains']:
                assert needle in resp.data.decode("utf-8")

        # Validate expected strings do not appear in response
        if 'excludes' in pages:
            for needle in page['excludes']:
                assert needle not in resp.data.decode("utf-8")
