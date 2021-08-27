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
from ast import literal_eval
from requests.exceptions import RequestException
from flask import request
from sandhill import app
from sandhill.utils.config_loader import load_json_config
from sandhill.utils.api import api_get
from sandhill.utils import jsonpath
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
        TODO
    """
    try:
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
    return jsonpath.find(json_resp, struct['path'])

def prepare_page_entry(page_entry):
    """
    Load the instance/tests/pages.json and queue up
    functional tests on each entry within the file
    """
    pages = []
    data = page_entry['data'] if 'data' in page_entry else {}
    loop = data['loop'] if 'loop' in data else None
    # Temporarily remove 'evaluate' while we prepare entry (to prevent early Jinja evaluation)
    evaluates = None
    if 'evaluate' in page_entry:
        evaluates = page_entry['evaluate']
        del page_entry['evaluate']

    # For each entry in the loop we'll perform a page_entry test; or loop of None if no loop defined
    loop_recs = jsonpath_from_rendered_url(data[loop], copy.deepcopy(page_entry)) if loop else [None]
    # Ensure our query found a list and it's not empty
    assert loop_recs
    assert isinstance(loop_recs, list)
    for rec in loop_recs:
        # First we'll need to create a copy of the page_entry
        loop_page = copy.deepcopy(page_entry)
        # Update our loop key to be the entry from the results of our loop query
        if rec:
            loop_page[loop] = rec

        # For any remaining keys in 'data', render Jinja and grab the URL/JSONPath results
        for key in (loop_page['data'] if 'data' in loop_page else {}):
            if key in ['loop', loop]:
                continue
            loop_page[key] = jsonpath_from_rendered_url(loop_page['data'][key], loop_page)

        # Perform one last Jinja render on the entire page_entry before running the test
        loop_page = render_template_json(loop_page, copy.deepcopy(loop_page))

        # Set extra allowed keys generated from 'data'
        loop_page['_extra_keys'] = list(data.keys()) + ['data']
        if 'loop' in loop_page['_extra_keys']:
            loop_page['_extra_keys'].remove('loop')

        # Re-add 'evaluate' key if set
        if evaluates:
            loop_page['evaluate'] = evaluates

        pages.append(loop_page)

    return pages

# Setup parameters for test_page_call
pages_conf = os.path.join(app.instance_path, "config/testing/pages.json")
page_entries = load_json_config(pages_conf)
pages = []
for entry in page_entries:
    pages.extend(prepare_page_entry(entry))

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
def test_page_call(page):
    """
    Run a single page test
    args:
        page (dict):
    """
    with app.test_client() as client:
        app.logger.info(f"Functional page test context: {dict(page)}")
        resp = client.get(page['page'])
        assert resp.status_code == page['code']

        # Check for mistakes or typo
        test_keys = page.keys()
        for test in test_keys:
            assert test in [
                '_comment', '_extra_keys', 'page', 'code', 'contains',
                'excludes', 'matches', 'evaluate', 'md5', 'data'
            ] + (page['_extra_keys'] if '_extra_keys' in page else [])

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

        # Validate Jinja evaluations
        if 'evaluate' in page:
            for check in page['evaluate']:
                check = check.strip()
                # Auto-add Jinja brackets if none are present
                if check == check.strip('{}'):
                    check = f"{{{{ {check.strip('{}')} }}}}"
                assert literal_eval(render_template_string(check, page))
