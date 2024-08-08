Instance Setup
==============

What is an instance?
--------------------
An instance is where you actually start developing your application. It contains all of the processing
you might do as well as the design of your pages. All of these build upon the already included
core Sandhill feature sets. Out of the box, Sandhill provides a range of data processors and Jinja2
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
[sandhill.default_settings.cfg](https://github.com/MSU-Libraries/sandhill/blob/master/sandhill/sandhill.default_settings.cfg)
file in the `sandhill/` directory.  

### `bootstrap/`
Each file within this directory should contain code to be run at start-up.  

For example:  
`instance/bootstrap/hi.py`:  
```python
print("Bootstrap test")
```
Which would add "Bootstrap test" to the start-up logs. A real world example would be if
you need to compile SCSS.  

### `commands/`
This directory is used to include additional [Click commands](https://flask.palletsprojects.com/en/1.1.x/cli/#custom-commands)
to your application.

For example:  
`instance/commands/hi.py`:
```python
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
not match a route will return a 404 page. Most routes are configured to render a 
Jinja2 _template_ (typically resulting in an HTML page), but can
also return a _stream_ of data (such as an image or downloadable file), or even use a _processor_
built to return a response that doesn't conform to either of the above. See the 
[routes](/sandhill/routes) documentation for more details and examples.

### `filters/`
Files within this directory are loaded to add  to the [default set of filters](#TODO)
already included in Sandhill.

Each filter will be available to all templates used within the application.

An example filter:
`instance/filters/myfilter.py`:
```python
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
the page then you might have a `database` processor. See the [data processors](/sandhill/data-processors)
documentation for further details and examples.

### `static/`
This directory contains any static content used by your application, such as CSS or JS files.

### `templates/`
The `templates` directory contains Jinja2 template files that can be referenced by your route
configs. They have the ability to access the built-in or custom filters and all of the variables
made available by your route configs (referenced by the `name` of the data item).
Refer to the examples within the [routes](/sandhill/routes) documentation to see the available variables.

You can see the
[default included template](https://github.com/MSU-Libraries/sandhill/blob/master/sandhill/templates/home.html.j2)
to start with, but see
[Jinja2 documentation](https://jinja.palletsprojects.com/en/2.11.x/) for the full range of options.
