Instance Setup
==============

What is an instance?
--------------------
An instance is where you actually start developing your application. It contains all of the processing
you might do as well as the design of your pages. All of these build upon the already included
core Sandhill feature sets. Out of the box, sandhill provides a range of data processors and Jinja2
template filters; but one has a simple "It Works!" template. It is up to you to develop everything
in between to make your application have the feature set you desire! Think of it as Sandhill providing
the core framework and your instance is your implementation of an application using that framework.

Basic structure of the instance directory
------------------------------------------
All of the files in the below directories are dynamically loaded without additional
configuration needed. None of these directories require files to be present
for the site to load, but are used to add functionality to it.  

instance/  
├── sandhill.cfg  
├── bootstrap/  
├── commands/  
├── config/  
│   └── routes/  
├── filters/  
├── static/  
└── templates/  

### `sandhill.cfg`
Configuration parameters can be passed either in a config file or via environment variables on the host machine.
Environment variables either at the host level (in `/etc/environment`) or at the application level (in a 
`.env` in the same directory as where the `instance/` directory is).  

To see what default values will be used if none are passed, see the 
[sandhill.default_settings.cfg](sandhill.default_settings.cfg) file in the `sandhill/` directory.  

### `bootstrap/`
Each file within this directory should contain code to be run at start-up.  

For example:  
`instance/bootstrap/hi.py`:  
```
print("Bootstrap test")
```
Which would add "Bootstrap test" to the start-up logs. A real world example would be if
you need to compile SCSS.  

### `commands/`
This directory is used to include additional [Click commands](https://flask.palletsprojects.com/en/1.1.x/cli/#custom-commands)
to your application.

For example:  
`instance/commands/hi.py`:
```
import click
from sandhill import app

@app.cli.command("hi")
@click.argument("name")
def hi(name):
    print(f"Hi {name}!")
```
Would allow you to run:
```
$ flask hi bob
Hi bob!
```

### `config/routes/`
A _route_ defines a URL pattern that Sandhill will match. Any request to Sandhill that does
not match a route will return a 404 page.

Most routes are configured to render a Jinja2 _template_ (typically resulting in an HTML page), but can
also return a _stream_ of data (such as an image or downloadable file), or even use a _processor_
built to return a response that doesn't conform to either of the above.

To create a new route, create a uniquely named `.json` file inside `instance/config/routes/`. JSON files
in this directory will be automatically loaded _when Sandhlll is started_ (note, adding new routes requires
restarting of Sandhill).

The `routes` directory is nested under `config` so that you can use the `config` directory for other items within
your application as well.

An example route config file might look like this:  
`instance/config/routes/mypage.json`:
```
{
    "route": [
        "/about",
        "/about/<string:context>"
    ],
    "template": "about.html.j2",
    "data": [
        {
            "name": "staff",
            "processor": "db.about_staff",
            "params": {
                "page_context": "{{ view_args.context }}"
            }
        },
        {
            "name": "unit",
            "processor": "db.unit_contact_info",
            "params": {
                "page_context": "{{ view_args.context }}"
            }
        }
    ]
}
```

An example route config that streams output might look like:  
`instance/config/routes/mystream.json`:
```
{
    "route": "/iiif/<string:pid>",
    "data": [
        {
            "processor": "iiif.load_image",
            "name": "iiif",
            "identifier": "{{ view_args.pid }}"
        },
        {
            "processor": "stream.stream",
            "stream": "iiif",
            "name": "stream"
        }
    ]
}
```


#### Config Attributes

`route`  
_Type_: string, or list of strings  
_Desc_: The URL pattern to match in order for this route to be selected. May be a single route or
a list of multiple routes. If any of the routes at matched, this route config will be used to
handle the request. Variables may be defined in the route using the `<myvariable>` syntax.
See [Flask documentation on routes](https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing)
for more information. Variables defined in the route will be available for use by data _processors_
and templates inside the variable name `view_args`, e.g. `view_args.myvariable`.  

`template` (optional)  
_Type_: string  
_Desc_: The name of the Jinja2 template file to attempt to render. The results of all defined data
_processors_ will be passed to this template. The result of this template will be rendered out
to the user. Jinja is a very powerful templating engine; for more info see the official
[Jinja2 documentation](https://jinja.palletsprojects.com/en/2.11.x/).   

`response` (optional)  
_Type_: string  
_Desc_: Specify the name of one data _processor_ to return directly, if the _processor_ allows it.
This is for more advanced usage, for example returning a JSON response directly.  

`data` (optional)  
_Type_: list of JSON objects (each containging name/value pairs)  
_Desc_: An ordered list of data _processors_, with each one being run in order. Each entry inside
`data` may make reference to all previous entries, so one results is able to use the results of the
last as part of its parameters. Processors may have custom parameters accepted, depending on the
_processor_ called; see the documentation for each _processor_ for further details. Required
arguments inside each entry are: `name` and `processor`.  

_Arguments for each `data` Object_  
* `name` (string): The name of the variable in which to store the results of this data _processor_. This name will appear as a variable inside temapltes.  
* `processor` (string): The filename and function to call as the data processor, e.g. `solr.select_record` would load the `solr.py` processor and call the `select_record` function.  
* `on_fail` (int, optional): The HTTP status code number to abort the page render with, should the data _processor_ fail in any way.  
* `stream` (string, optional): Used to identify what variable to stream (instead of rendering a template). The value in `steam` should match the `name` of another `data` element that comes before it.  
* `?` (all other arguments): Dependent on the _processor_; refer to that specific _processor_ documentation for details.  


### `filters/`
Files within this directory are loaded to add  to the [default set of filters](sandhill/utils/filters.py)
already included in Sandhill.

Each filter will be available to all templates used within the application.

An example filter (which is one of the default set):
`instance/filters/myfilter.py`:
```
from sandhill import app

@app.template_filter()
def islist(value):
    """ Check if a value is a list """
    return isinstance(value, list)
```

Would provide the ability to do this in your template:
`instance/templates/home.html.j2`:
```
...
<p>Is myvar a list? {{ myvar | is_list }}</p>
...
```

### `processors/`
Processors are what are called in the route configs to provide data or data processing before rendering a
template or streaming output. For example if your home page requires you make a database call to get information for
the page then you might have a `database` processor. An example of one of the [built-in processors](sandhill/processors)
is the `file` processor; which has a function called `load_json`. This would allow us to reference it in the
data section of a route config by saying `file.load_json`.

All processors must take the argument of `data_dict`. This is a special variable that contains all of the data
from previously loaded processors. So if your route config has 2 data processors called, the second one would have access
to the output of the first one. Additionally, arguments from the original request are available (such as the url arguments).

Example route config and corresponding `data_dict` values:
`instance/config/routes/home.json`:
```
"route": [
        "/home",
        "/home/<string:name>"
    ],
    "template": "home.html.j2",
    "data": [
        {
            "name": "myset",
            "processor": "file.load_json",
            "paths": ["config/home/set1.json"]
        }
    ]
...
```
`config/home/set1.json`:
```
{
    "var1": 1
}
```

`data_dict` after the `myset` data has been loaded (which would in turn be available
to subsequently listed `data` items):
```
{
    "view_args": {
        "name": "bob"
    },
    "paths": ["config/home/set1.json"],
    "myset": {
        "var1": 1
    }
}
```

### `static/`
This directory contains any static content used by your application, such as CSS or JS files.

### `templates/`
The `templates` directory contains Jinja2 template files that can be referenced by your route
configs. They have the ability to access the built-in or custom filters and all of the variables
made available by your route configs (referenced by the `name` of the data item). See the example
within the [processors](#processors) section of what the `data_dict` looks like to see all of the
available variables.

You can see the [default included template](sandhill/templates/home.html.j2) to start with, but see
[Jinja2 documentation](https://jinja.palletsprojects.com/en/2.11.x/) for the full range of options.
