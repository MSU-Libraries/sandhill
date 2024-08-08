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
setting up your Sandhill instance](./instance-setup.md)). Specifically, route files should
be placed in `instance/config/routes/`. Sandhill will automatically load all `.json`
files placed here when it starts.

### A Simple Example
A simple example route file might look like this:
```json title="instance/config/routes/simple.json"
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

Sandhill comes with a number of [builtin data processors](./data-processors.md)
that can be used immediately, though with some knowledge of Python programming
[you can also define your own data processors](./data-processors.md#developing-a-data-processor).


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
[data processor documentation](./data-processors.md#sandhill.processors.solr)
and details on how to configure Sandhill is available in the
[instance setup documentation](./instance-setup.md).

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

### Conditional Data Processors and Implied Template

Here is a more advanced route example that shows how you can use the 
`when` attribute. 

```json hl_lines="10"
{
    "route": [
        "/item/<int:id>"
    ],
    "data": [
        {
            "name": "render-id1",
            "processor": "template.render",
            "file": "item1.html.j2",
            "when": "{{ view_args.id == 1 }}"
        },
        {
            "name": "render",
            "processor": "template.render",
            "file": "item.html.j2"
        }
    ]
}
```
In this example, notice that there is no `template` attribute provided.
When a data processor returns a
[FlaskResponse](https://flask.palletsprojects.com/en/latest/api/#flask.Response)
or
[WerkzeugReponse](https://werkzeug.palletsprojects.com/en/latest/wrappers/#werkzeug.wrappers.Response),
Sandhill will stop processing any further data processors and return that response immediately.
In fact, specifying the `template` attribute is really just a shorthand method of appending the
`template.render` processor as seen above.

The `when` condition in the example is showing how you can conditionally have
a data processor excluded from running when a page is loaded if the `when` condition is `True`.
In this case the condition is based on one of the route URL variables (`view_args.id`),
but all loaded data is available. A `when` is considered `True` if the value would be considered
true [when evaluated in Python](https://docs.python.org/3.10/library/stdtypes.html#truth-value-testing).

### Error Handling

By default, Sandhill will not stop processing a request if a data processor fails or
returns no data. When this is not desired, the `on_fail` may be set for any given
data processor.

Setting the `on_fail` to a [HTTP status code integer](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes)
will cause Sandhill to abort with that code should that data processor fail to return any data.
```json hl_lines="11"
{
    "route": [
        "/item/<int:id>"
    ],
    "template": "record.html.j2",
    "data": [
        {
            "name": "record",
            "processor": "solr.select_record",
            "params": { "q": "ID:{{ view_args.id }}" },
            "on_fail": 404
        }
    ]
}
```

With the above configuration, if the call to Solr fails for any reason,
a 404 error will be returned and the abort template will be displayed instead.
When the `on_fail` is not set and a failure occurs in a data processor, those
errors are simply recorded in the logs and the next processor is loaded.
Setting this attribute allows more fine-grained control over what processors
are critical to a page loading and what error is appropriate for those errors.

Some data processors have the ability to return
the HTTP code of its choice. For example, if the data processor is making an
external API call and you'd prefer it to pass back the HTTP code from the API call
on failure. If the data processor supports it, setting `on_fail` to `0` will
accomplish this. The `0` value indicates that Sandhill should abort page processing
on a failure, but leave the selection of HTTP code up to the data processor.

## Route Config Attributes
This section contains a summary of the available attributes for route definitions for
quick reference. But more details on any of these attributes are found above.
For full details on the `data` section, see the [data processors documentation](data-processors.md).

| Name  | Type                       | Description |
|-------|----------------------------|-------------|
| `route` | string, or list of strings | The URL pattern to match in order for this route to be selected |
| `template` | string, optional | The name of the Jinja2 template file to attempt to render |
| `data` | list of JSON entries, optional | An ordered list of data processors, with each one being run in order |
