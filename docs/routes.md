# Routes in Sandhill
Sandhill processes page requests by looking at the path provided in the URL.
The path of the URL is the part between the hostname and the arguments.

For example, with the URL:
```
https://example.edu/collection/42?sort=desc
```

The path would be: `/collection/42`

If Sandhill has a route defined that matches a requested path, it would proceed
to render the appropriate page based on the defined route.

## Defining a Route
Routes are defined as JSON files inside your instance directory (see the [guide on
setting up your Sandhill instance](#TODO)). Specifically, route files should
be placed in `instance/config/routes/`. Sandhill will automatically load all `.json`
files placed here when it starts.

### A Simple Example
A simple example route file might look like this:
```json
{
    "route": [
        "/collections/",
        "/browse/"
    ],
    "template": "collections.html"
}
```

In the above definition, going to either URL for your site:
```
https://example.edu/collections/
https://example.edu/browse/
```

Would serve up the `collections.html` file from your instance templates directory.
Per the standard setup, all HTML templates should be placed in `instance/templates/`.

Route definitions follow the [Flask routing](https://flask.palletsprojects.com/en/2.1.x/quickstart/#routing)
mechanics. Flask is the framework which underpins Sandhill.

### Variables in Route Path
This supports putting variables into the path such as
`/collections/<int:collection_id>/` which can be referenced
while the page is processing. In Sandhill, these path arguments are made available
by the `view_args` variable; in such that `view_args.collection_id` would be
the value `42` if the path was `/collections/42/`.

Flask provides the following variable types:

| type | example path | description |
|----|----|-----------|
| `string` | `/list/<string:namespace>/` | Any string of text without slashes (`/`) |
| `int` | `/db/<int:db>/row/<int:row>` | Positive integer values |
| `float` | `/round/<float:num>` | Positive decimal values |
| `path` | `/dir/<path:subdir>` | Any string, including slashes (`/`) |
| `uuid` | `/account/<uuid:account>/` | A [Universally unique identifier](https://en.wikipedia.org/wiki/Universally_unique_identifier) string |

## Route with Data Processors
A core feature of Sandhill is how it handles loading additional data while it
processes a route. These additional actions are defined in the same route file
and call upon Sandhill **data processors** to perform specific actions.

A data processor can load dynamic data from a datastore or manipulate
already loaded data to prepare it for output to the user.

Sandhill comes with a number of [builtin data processors](data-processors.md)
that can be used immediately, though with some knowledge of Python programming
[you can also define your own data processors](#TODO).


### Example with a Data Processor
Here's a basic route which uses a data processor to query a Solr service
and retrieve a record:
```json
{
    "route": [
        "/hello/<int:user_id>"
    ],
    "template": "hello.html.j2",
    "data": [
        {
            "name": "user",
            "processor": "solr.select_record",
            "params": { "q": "user_id:{{ view_args.user_id }}" }
        }
    ]
}
```

With the HTML template file containing Jinja2 syntax:
```html
<!DOCTYPE html>
<html>
<body>
    <h1>Hello to {{ user.firstname }} {{ user.lastname }}!</h1>
    <p>{{ user.firstname }}'s user_id is {{ user.user_id }}.</p>
</body>
</html>
```

A request to `https://example.edu/hello/33` might produce and response like:
```html
<!DOCTYPE html>
<html>
<body>
    <h1>Hello to Aaron Zahn!</h1>
    <p>Aaron's user_id is 33.</p>
</body>
</html>
```

In this case, the `solr.select_record` data processor automatically pulls the
appropriate Solr API base URL from either the `instance/sandhill.cfg` file or
from an environment variable, both named `SOLR_URL`. More details on the
`solr` data processor is available in the
[data processor documentation](/data-processors/#sandhill.processors.solr)
and details on how to configure Sandhill is available in the
[setup documentation](#TODO).

## Jinja Templating
Regarding the HTML template, Sandhill makes full use of the [Jinja2 templating
engine](https://jinja.palletsprojects.com/en/3.1.x/templates/) for rendering
pages.

It's not just HTML templates that are Jinja processed. Data processor definitions
in the route config files are Jinja rendered as well. So the following is possible:
```json
{
    "route": [
        "/<string:namespace>/<int:id>"
    ],
    "template": "record.html.j2",
    "data": [
        {
            "name": "record",
            "processor": "solr.select_record",
            "params": { "q": "rec:{{ view_args.namespace }}-{{ view_args.id }}" }
        },
        {
            "name": "parent",
            "processor": "solr.select_record",
            "params": { "q": "rec:{{ record.parent_rec }}" }
        }
    ]
}
```

Notice how use of Jinja is available in the JSON `data` section. Jinja expressions
are rendered on a per request basis. Sandhill always provides
the `view_args` variable for use of route path variables. Beyond that, any variables
defined by a data processor also becomes available after that processor has run.

In the previous example, notice how the second data processor is referencing the result
of the first data processor (i.e. `record`).

This is possible because **data processor definitions are rendered in Sandhill sequentially**.
Each data processor is able to make use of data created by the processors defined before it.

!!! warning "Mixing Jinja and JSON"

    If use of Jinja expressions results in invalid JSON, the route will become unparsable.
    Be careful when using Jinja in JSON and ensure your output is JSON compatible.
    If your route is failing to load, be sure to check the Sandhill logs.

## Advanced Examples
- Provide at least 2 more advanced route examples with explainations
- Use of `when`
- Example showing that `template` is just a shortcut for adding an ending `template` data processor

## Route Config Attributes
This section contains a summary of the available attributes for route definitions for
quick reference. But more details on any of these attributes are found above.

* `route` (string, or list of strings): The URL pattern to match in order for
this route to be selected. May be a single route or
a list of multiple routes. If any of the routes at matched, this route config will be used to
handle the request. Variables may be defined in the route using the `<type:varname>` syntax.
See [Flask documentation on routes](https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing)
for more information. Variables defined in the route will be available for use by data _processors_
and templates inside the variable name `view_args`, e.g. `view_args.varname`.  

* `template` (string, optional: The name of the Jinja2 template file to attempt
to render. The results of all defined data _processors_ will be passed to 
this template. The result of this template will be rendered out
to the user. Jinja is a very powerful templating engine; for more info see the official
[Jinja2 documentation](https://jinja.palletsprojects.com/en/3.1.x/).   

* `variables` (dict, optional): User defined variables that are not validated in the
JSON schema. May be used for custom instance functionality.

* `response` (string, optional): Specify the name of one data _processor_ to return
directly, if the _processor_ allows it. This is for more advanced usage, for example 
returning a JSON response directly.  

* `data` ([list of JSON objects](#data-processor-config-attributes), optional): An ordered list
of data _processors_, with each one being run in order. Each entry inside
`data` may make reference to all previous entries, so one results is able to use the results of the
last as part of its parameters. Processors may have custom parameters accepted, depending on the
_processor_ called; see the documentation for each _processor_ for further details. Required
arguments inside each entry are: `name` and `processor`.  

## Data Processor Config Attributes  
This section lists the available attributes that can be set for each `data` section
defined in a route config.

* `name` (string): The name of the variable in which to store the results of this data _processor_. This name will appear as a variable inside temapltes.  
* `processor` (string): The filename and function to call as the data processor, e.g. `solr.select_record` would load the `solr.py` processor and call the `select_record` function.  
* `on_fail` (int, optional): The HTTP status code number to abort the page render with, should the data _processor_ fail in any way.  
* `stream` (string, optional): Used to identify what variable to stream (instead of rendering a template). The value in `steam` should match the `name` of another `data` element that comes before it.  
* `?` (all other arguments): Dependent on the _processor_; refer to that specific _processor_ documentation for details.  
