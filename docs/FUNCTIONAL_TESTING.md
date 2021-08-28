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
* `_comment` (Optional) Gives you a place to describe the purpose of the test.
* `page` The relative page on your site to call and test against
* `code` (Optional) The HTTP code the request to your page should return.
* `contains` (Optional, List) A list of strings that should exist in the source code returned for the page.
* `excludes` (Optional, List) A list of strings that should NOT exist in the source code returned from the page.

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

The `instance/testing/pages.json` file is JSON where the root object must be a list. An empty file
would appear like:
```
[]
```

Adding entries into list must follow a dict stype format and may have the following keys:  

**_comment**  
This is just a freeform field where you may add a description for the page test.  

**page**  
**code**  
**contains**  
**excludes**  
**matches**  
**data**  
**data[loop]**  
**data[????]**  
**evaluate**  

