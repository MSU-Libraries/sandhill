Functional Testing
===========

Sandhill allows you to create automated testing of your site pages, allowing fast
verification that your site is operating normally. Each test can verify any number
of apects of page (or pages) to ensure they are in compliance.

Basically, each test will perform an actual call to your instance of Sandhill and
then perform verification checks on the response. What verification checks it does
is entirely up to you.

Entry of functional tests are maintained in a JSON file at:
```
instance/config/testing/pages.json
```

The Basics
------
Here would be a fairly simple `pages.json` file with 3 test entries:
```
[
    {
        "_comment": "Ensure main page loads"
        "page": "/",
        "code": 200,
        "contains": [
            "Welcome to my site!"
        ]
    },
    {
        "_comment": "Access to user profiles should be rejected unless authenticated"
        "page": "/user/1/profile",
        "code": 401
    },
    {
        "_comment": "The order form should be empty by default",
        "page": "/order/cart",
        "code": 200,
        "contains": [
            "Your cart (0 items)"
        ],
        "excludes": [
            "Remove from cart",
            "Proceed to checkout"
        ]
    }
]
```

Breaking these tests down:
* `_comment` Gives you a place to describe the purpose of the test.
* `page` The relative page on your site to call and test against
* `code` The HTTP code the request to your page should return.
* `contains` A list of strings that should exist in the source code returned for the page.
* `excludes` A list of strings that should NOT exist in the source code returned from the page.

For each page entry, all specified tests much succeed or the entire entry will fail.  

To run all your functional tests, issue the command:  
```
INSTANCE_DIR=/opt/sandhill/instance /opt/sandhill/env/bin/pytest -m functional --no-cov
```
Given that:  
* `/opt/sandhill/instance` is where your `instance` directory is located
* `/opt/sandhill` is where Sandhill is installed.

Of course, update these to match your setup.  

If all goes well, the output would look like this:
```
========================== test session starts =============================
platform linux -- Python 3.6.9, pytest-6.0.1, py-1.10.0, pluggy-0.13.1
rootdir: /opt/sandhill, configfile: pytest.ini
plugins: cov-2.10.0, mock-3.3.1
collected 85 items / 82 deselected / 3 selected

sandhill/tests/test_pages.py ...                                      [100%]

==================== 3 passed, 82 deselected in 32.11s =====================
```

You will see the 3 dots next to the `test_pages.py` entry along with 3 tests selected
and 3 test passed. The other tests (82 in the example above) are unit tests used by Sandhill
developers to test internal code. It's okay for those to be deselected.  

That's the basics to get started. First create the `pages.json` file and then start adding
tests to it. Keep reading if you'd like to learn about the more advanced capabilities available.  


Advanced Usage
------

JSON files located in `instance/testing/` will be loaded for testing. The root object must be a list,
that is, an empty file would appear like:
```
[]
```

Adding entries into list must follow a dict type format and may have the following keys:  

**_comment** (Optional, String, Jinja Processed)  
This is just a freeform string field where you may add a description for the page test.  

Examples:  
`"_comment": "Check that all embargoed items cannot be downloaded"`  
`"_comment": "Verify disclaimer appears on all form pages"`  
`"_comment": "Checking asset links for {{ item.asset_id }}"`  

**page** (String, Jinja Processed)  
This is the relative link on which the page test will occur. An actual call to this page
happen as part of the test. If left blank, no page call will occur.  

Examples:  
`"page": "/node/aboutus"`
`"page": "/asset/{{ item.asset_id }}/view"`

**code** (Optional, Integer)  
The expected HTTP status code to receive as part of the response for the page call. Ignored
if no `page` was set.  

Examples:  
`"code": 200`
`"code": 403`

**contains** (Optional, List, Jinja Processed)  
A list of strings that must exist in the source code returned from the `page` called. All
entries must exist or the test will fail. Ignored if no `page` was set.  

Examples:  
```
"contains": [
    "<a href=\"#required\">Required Resources</a>",
    "Copyright &copy; MySandhill"
]
```
```
"contains": ["Request a consultation on {{ record.description }}"]
```

**excludes** (Optional, List, Jinja Processed)  
A list of strings that must NOT exist in the source code returned from the `page` called. None
of the entries may exist or else the test will fail. Ignored if no `page` was set.  

Examples:  
```
"excludes": [
    "/user/login",
    "/asset/{{ item.asset_id }}/download"
]
```
```
"excludes": ["555-1234"]
```

**matches** (Optional, List, Jinja Processed)  
A list of strings containing regular expressions that must match in the source code returned from
the `page` called. All of the entry patterns much match or else the test will fail.
 Ignored if no `page` was set.  

Examples:  
```
"matches": [
    "Copyright Status:\\s+In Copyright",
    "{{ user.fullname }}\\s+\\d{4}"
]
```
```
"matches": ["\\d{3}-\\d{4}"]
```

**data** (Optional, Dict)  
The `data` part of a test entry defines supplimental JSON data calls to make which can be used
in Jinja procesing, including during `evaluate` checks.  

An example `data` section could look like:
```
"data": {
    "loop": "item",
    "item": {
        "url": "{{ 'SOLR_URL' | getconfig }}/select?q=status:active&fl=asset_id,title&rows=999999",
        "path": "$.response.docs[*]"
    },
    "child": {
        "url": "{{ 'SOLR_URL' | getconfig }}/select?q=asset_id:{{ item.asset_id }}&fl=asset_id,title&rows=1",
        "path": "$.response.docs[0]"
    }
}
```

The only reserved key in a `data` section is `loop`. All other keys (`item`, `child` in the above example)
are defined with a `url` and `path` to perform and parse a JSON call. For this documentation, these other
keys will referred to as the variable `VAR`.  

**data[VAR]** (Optional, Dict, Jinja Processed)  
Where `VAR` is any user defined string, the value must be a dict that defines another JSON API call to
make and parse. Each `VAR` dict must have both `url` and `path` keys defined. There may be any number
of `VAR` keys, which are processed in the order they are defined (unless a `data[loop]` is defined, in
which the `VAR` indicated by the `loop` is always processed first.  

The results of a `data[VAR]` call will be stored in the page entry using the `VAR` key. The response
will be a list of matches, unless the response is indicated by `loop`, in which the `VAR` will be a
single entry from the response, but there will be a new page entry for each entry in the response
as well.  

For example, this entry:
```
{
    "page": /asset/{{ item.asset_id }}",
    "code": 404,
    "data": {
        "loop": "item"
        "item": {
            "url": "{{ 'SOLR_URL' | getconfig }}/select?q=status:disabled&fl=asset_id,title&rows=999999",
            "path": "$.response.docs[*]"
        }
    },
    "excludes": ["{{ item.title }}"]
}
```

Could result in a page entry to test for each record in `item`:
```
{
    "page": /asset/1",
    "code": 404,
    "item": {"asset_id": 1, "title": "My First Widget"},
    "excludes": ["My First Widget"]
},
{
    "page": /asset/2",
    "code": 404,
    "item": {"asset_id": 2, "title": "My Second Widget"},
    "excludes": ["My Second Widget"]
}
... (and additional page tests for each record matched by "item" URL and path)
```

**`data[VAR][url]`** (Optional, String, Jinja Processed)  
The `url` inside a `data[VAR]` dict defines a valid URL to call. The response must be in JSON format.
The response is then queried by `path` to get a subset of the JSON.  

**`data[VAR][path]`** (Optional, String, Jinja Processed)  
A JSONPath query to parse the JSON response from `url` to select a subset of data. The results of this
JSONPath query will be set into the page test entry under the key `VAR`.  

**`data[loop]`** (Optional, String)  
The `loop` key in `data` must have a value that indicates another `VAR` key in `data` which must also be
defined. The response from this targeted `VAR` will be looped over, generating a new page test entry
for each item in the target `VAR`.  

**`evaluate`** (Optional, List, Jinja Required)  
A list of strings that will be rendered by Jinja and then evaluated for truthiness. If the strings in
the list are not wrapped by Jinja delimiters, the `{{` and `}}` delimiters will automatically be wrapped
around the value. All entries must evaluate to a truthy value after having be Jinja processed or
the test will fail. You must have set a `data` section in order to have data to evaluate on.  

Values in an evaluate string are first parsed for JSONPath queries. Queries must begin with a
root indictor `$`. If no context key is provided, it will query against the first data key available.
To specify a JSONPath query to operate on a specific key, add the key name directly after
the `$`, such as `$item.myquery`.  

Examples:  
```
"evaluate": [
    "item.namespace == child[0].namespace",
    "child[0].collection in item.collections"
    "$item.response.numFound == $item.facet_counts.facet_fields.collection[1]"
```
```
"evaluate": ["{{ page | lower == page }}"]
```

Jinja Processing
------
Any field that is Jinja processed has access to all filters and context processors from Sandhill.
The context variables will be the entire page entry processed thus far.  

Jinja processing occurs in steps, with each step having access to the data already processed in
previous steps. Processing order is:
* The `data[VAR]` indicated by `data[loop]`.
* Each remaining `data[VAR]` in order of definition.
* The entire page entry, minus the `evaluate` key.
* The `evaluate` key (which occurs only during actual testing).

Advanced Examples
------
TODO

Accessiblity Testing
------
If you want to automcatically scan certain pages for accessibility violations, you
can include those as part of your functional testing configuration.

### Setup  
Get the [latest geckodriver](https://github.com/mozilla/geckodriver/releases) and install it in `/usr/local/bin`
```
wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz
tar -xf geckodriver-v0.30.0-linux64.tar.gz
sudo chown root:root geckodriver
sudo mv geckodriver /usr/local/bin/
```

Install firefox and Xvfb (the X windows virtual framebuffer)
```
sudo apt install firefox xvfb
```

Test that firefox is working
```
# set the number of displays
export DISPLAY=:2

# run xvfb in the background
Xvfb :2 -ac &
# start firefox to make sure it starts without errors (kill it with Ctrl-C)
firefox

# Now stop xvfb by returning the process to the forground and killing it (Ctrl-C)
fg
```

### Configuration  
Below is a sample entry for functional testing as seen earlier in this document.
Notice now the added key for `a11y`. Additionally, you can provide an optional `disable`
key which will ignore the provided list of Axe rules from the scan on that page.

For a complete list of available rules to exclude see the [official site](https://dequeuniversity.com/rules/axe/4.3).
```
    {
        "_comment": "Ensure main page loads"
        "page": "/",
        "code": 200,
        "contains": [
            "Welcome to my site!"
        ],
        "axe": {}
    },
    {
        "_comment": "Ensure second page loads"
        "page": "/page 2",
        "code": 200,
        "contains": [
            "Welcome to my page!"
        ],
        "axe": {
            "disable": ["landmark-main-is-top-level", "landmark-one-main"]
        }
    }
```
