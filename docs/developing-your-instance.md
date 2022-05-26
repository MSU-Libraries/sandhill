Development Guide
==================

See the following important documents to get started:

* [Code Standards](/code-standards)
* [Instance Setup](/instance-setup)

Creating your first page
------------------------

To get started building your own site using Sandhill, you will need to first
[create your instance](/instance-setup). That `instance` directory will
be where you start your development.

Once you have your base instance directory structure setup you are ready to start
writing `route` configs and their corrresponding `templates`.

When writing your route config you will have the ability to set the url patterns that
will resolve to that route config (ex: `\home` or `\item\<int:id>`) and then create
any number of data sections that can process input and getnerate output that can
either be streamed or sent to a template file. These data sections can use any of the
processors included with Sandhill or ones developed by you in the `instance/processors`
directory.

Assuming you've created a route that will resolve to a template, you can now move
on to making that template with a name that matches what you provided in the route
config. In that template, you will have full access to all Jinja2 filters and as well
as all of the filters in Sandhill. See the
[official documentation](https://jinja.palletsprojects.com/en/2.11.x/templates/)
for a more complete list of what you can do within Jinja. If you find a need for additional filters,
you can add them in `instance/filters`.

Testing
-------

Of course a very important part of any application is testing. Sandhill has included unit tests for
all of it's components and we strongly encourage you to do the same for any custom components
you write for your `instance`. These files should start with `test_` and be within a sub-directory
called `tests` inside each relavent (ex: `instance/filters/tests/test_myfilter.py`).

To run the unit tests simply run:
```
env/bin/pytest
```

If you'd like to include functional tests for your pages, you can create a `instance/tests/pages.json`
file which contains pages you'd like to test the responses from.

An example of a few of those tests would be:
```
[
    {
        "page": "/",
        "code": 200,
        "contains": [
            "It Works!"
        ]
    },
    {
        "_comment": "Testing that no errors appeared on the page"
        "page": "/mypage",
        "code": 200,
        "excludes": [
            "<p>Error</p>"
        ]
    },
    {
        "page": "/path/does/not/exist",
        "code": 404
    }
]
```

To run the functional tests:
```
env/bin/pytest -m functional
```

Contributing
-------------
If you feel any of the utilities you've written in your `instance` would be useful
for other users in the community, you have the option of
[contributing back](https://github.com/MSU-Libraries/sandhill/blob/master/CONTRIBUTING.md)
to Sandhill.
