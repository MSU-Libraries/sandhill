'''
Runs functional tests
'''
import os
import re
import pytest
import json
import hashlib
import collections
import jinja2
import json
import copy
from urllib.parse import urljoin
from selenium import webdriver
from axe_selenium_python import Axe
from ast import literal_eval
from requests.exceptions import RequestException
from flask import request
from sandhill import app
from sandhill.utils.config_loader import load_json_config
from sandhill.utils.api import api_get
from sandhill.utils import jsonpath
from sandhill.utils.generic import getconfig
from sandhill.utils.template import render_template_json, render_template_string

def jsonpath_from_rendered_url(struct, context):
    """
    Render a dict structure using Jinja and then
    perform an API call to 'url' key.
    For the resulting JSON, select and return
    the data found at the JSONPath 'path' key
    args:
        struct(dict): A data structure with keys
                        url => Location to perform API call
                        path => A JSON path
        context(dict): The context used to render with Jinja
    returns:
        (dict|list): The results of the JSONPath
    throws:
        json.JSONDecodeError
        jinja2.TemplateError
        requests.exceptions.RequestException
    """
    try:
        with app.app_context():
            struct = render_template_json(struct, context)
    except (json.JSONDecodeError, jinja2.TemplateError) as exc:
        app.logger.error(f"Unable to render and convert: {struct}")
        raise exc
    try:
        resp = api_get(url=struct['url'])
        json_resp = json.loads(resp.content)
    except (RequestException, json.JSONDecodeError) as exc:
        app.logger.error(f"Failure to retrieve JSON from URL: {struct['url']}")
        raise exc
    struct['path'] = struct['path'] if 'path' in struct else None
    return jsonpath.find(json_resp, struct['path'])

def prepare_test_entry(entry):
    """
    Load and entry for testing and queue up the resulting
    tests generated from the entry.
    """
    tests = []
    data = entry['data'] if 'data' in entry else {}
    loop = data['loop'] if 'loop' in data else None
    # Temporarily remove 'evaluate' while we prepare entry (to prevent early Jinja evaluation)
    evaluates = None
    if 'evaluate' in entry:
        evaluates = entry['evaluate']
        del entry['evaluate']

    # For each entry in the loop we'll perform a entry test; or loop of None if no loop defined
    loop_recs = jsonpath_from_rendered_url(data[loop], copy.deepcopy(entry)) if loop else [None]
    # Ensure our query found a list and it's not empty
    assert loop_recs
    assert isinstance(loop_recs, list)
    for rec in loop_recs:
        # First we'll need to create a copy of the entry
        loop_entry = copy.deepcopy(entry)
        # Update our loop key to be the entry from the results of our loop query
        if rec:
            loop_entry[loop] = rec

        # For any remaining keys in 'data', render Jinja and grab the URL/JSONPath results
        for key in (loop_entry['data'] if 'data' in loop_entry else {}):
            if key in ['loop', loop]:
                continue
            loop_entry[key] = jsonpath_from_rendered_url(
                loop_entry['data'][key],
                copy.deepcopy(loop_entry)
            )

        # Perform one last Jinja render on the entire entry_entry before running the test
        with app.app_context():
            loop_entry = render_template_json(loop_entry, copy.deepcopy(loop_entry))

        # Set extra allowed keys generated from 'data'
        loop_entry['_extra_keys'] = list(data.keys()) + ['data']
        if 'loop' in loop_entry['_extra_keys']:
            loop_entry['_extra_keys'].remove('loop')

        # Re-add 'evaluate' key if set
        if evaluates:
            loop_entry['evaluate'] = evaluates

        tests.append(loop_entry)
    return tests

def get_test_configs():
    """
    Get a list of all testing config files from the instance config/testing/ directory
    """
    testing_confs = []
    testing_conf_dir = os.path.join(app.instance_path, "config/testing/")
    for root, dirs, files in os.walk(testing_conf_dir):
        for f in files:
            if f.endswith(".json"):
                testing_confs.append(os.path.join(root, f))
    return testing_confs

def load_tests():
    """
    Read in and parse all tests from the instance config/testing/ directory
    """
    tests = []
    for tcnf in get_test_configs():
        print(f"Loading tests from: {tcnf}")
        entries = load_json_config(tcnf)
        for entry in entries:
            tests.extend(prepare_test_entry(entry))
    return tests

test_entries = load_tests()

@pytest.mark.functional
@pytest.mark.metadata
@pytest.mark.a11y
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
def test_configs_loadable():
    """
    Validate JSON can be parsed if present
    """
    for tcnf in get_test_configs():
        with open(tcnf, 'r') as tests_conf:
            loaded = json.load(tests_conf, object_pairs_hook=collections.OrderedDict)
        assert isinstance(loaded, list)
        if len(loaded):
            assert isinstance(loaded[0], collections.OrderedDict)

@pytest.mark.functional
@pytest.mark.metadata
@pytest.mark.filterwarnings("ignore::pytest.PytestUnraisableExceptionWarning")
@pytest.mark.parametrize("entry", test_entries)
def test_entry_call(entry, pytestconfig):
    """
    Run a single test entry
    args:
        entry (dict):
    """
    mark = pytestconfig.getoption('-m')
    mark_functional = (mark == "functional")
    mark_metadata = (mark == "metadata")

    with app.test_client() as client:
        app.logger.info(f"Testing context: {dict(entry)}")
        # Check for mistakes or typo
        test_keys = entry.keys()
        for test in test_keys:
            assert test in [
                '_comment', '_extra_keys', 'page', 'code', 'contains',
                'excludes', 'matches', 'evaluate', 'md5', 'data', 'a11y'
            ] + (entry['_extra_keys'] if '_extra_keys' in entry else [])

        if mark_functional:
            if 'page' not in entry:
                pytest.skip("Not a valid functional test (no 'page')")

            resp = client.get(entry['page'])
            assert resp.status_code == entry['code']

            # Validate expected strings appear in response
            if 'contains' in entry:
                for needle in entry['contains']:
                    assert needle in resp.data.decode("utf-8")

            # Validate expected strings do not appear in response
            if 'excludes' in entry:
                for needle in entry['excludes']:
                    assert needle not in resp.data.decode("utf-8")

            # Validate matches against a regex string in the response
            if 'matches' in entry:
                for needle in entry['matches']:
                    assert re.search(needle, resp.data.decode("utf-8"))

            # Validate response content matches given md5
            if 'md5' in entry:
                hasher = hashlib.md5()
                hasher.update(resp.data)
                assert entry['md5'] == hasher.hexdigest()

        if mark_metadata:
            if 'evaluate' not in entry:
                pytest.skip("Not a valid metadata test (no 'evaluate')")

            # Validate Jinja evaluations
            if 'evaluate' in entry:
                for check in entry['evaluate']:
                    check = check.strip()
                    # Pre-parse JSONPath references
                    check = jsonpath.eval_within(check, entry)
                    # Auto-add Jinja brackets if none are present
                    if check == check.strip('{}'):
                        check = f"{{{{ {check.strip('{}')} }}}}"
                    assert literal_eval(render_template_string(check, entry))

@pytest.fixture(scope="session", autouse=True)
def axe_driver():
    try:
        with webdriver.Firefox() as driver:
            yield driver
    except:
        yield None

@pytest.mark.a11y
@pytest.mark.parametrize("entry", test_entries)
def test_entry_a11y(entry, axe_driver):
    """
    Run a single entry test
    args:
        entry (dict):
    """
    with app.test_client() as client:
        app.logger.info(f"Accessibility page test context: {dict(entry)}")
        # Validate page passes accessibility checks
        if 'a11y' not in entry:
            pytest.skip("Not a valid accessibility test (no 'a11y')")

        # Verify the driver was initialized
        assert axe_driver is not None

        axe_driver.get(urljoin("https://" + getconfig('SERVER_NAME'), entry['page']))
        axe = Axe(axe_driver)
        axe.inject()

        # https://github.com/dequelabs/axe-core/blob/master/doc/API.md#options-parameter
        options = ""
        if "disable" in entry['a11y'] and isinstance(entry['a11y']['disable'], list):
            options = "{ rules: {"
            for rule in entry['a11y']['disable']:
                options += f"'{rule}':{{ 'enabled': false }},"
            options += "} }"

        results = axe.run(options=options)

        sandbug(urljoin("https://" + getconfig('SERVER_NAME'), entry['page']))
        sandbug(results["violations"])
        assert len(results["violations"]) == 0, axe.report(results["violations"])
