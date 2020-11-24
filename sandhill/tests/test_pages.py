'''
Runs functional tests
'''
import os
import pytest
from sandhill.utils.config_loader import load_json_config
from sandhill import app

@pytest.mark.functional
def test_pages():
    """
    Load the instance/tests/pages.json and perform
    functional tests on each entry within the file
    """
    # TODO added checks around these
    pages_conf = os.path.join(app.instance_path, "tests/pages.json")
    pages = load_json_config(pages_conf)

    with app.test_client() as client:
        for page in pages:
            app.logger.info("Testing page: {0}".format(page['page']))
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
