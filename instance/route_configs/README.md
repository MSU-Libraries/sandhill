Route Configuration
==============================

A _route_ defines a URL pattern that Sandhill will match. Any request to Sandhill that does
not match a route will return a 404 page.  

Most routes are configured to render a Jinja2 _template_ (typically resulting in an HTML page), but can
also return a _stream_ of data (such as an image or downloadable file), or even use a _processor_
built to return a response that doesn't conform to either of the above.  

To create a new route, create a uniquely named `.json` file inside `instance/route_configs/`. JSON files
in this directory will be automatically loaded _when Sandhlll is started_ (note, adding new routes requires
restarting of Sandhill).  

And example route config file might look like this:  
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


Config Attributes
------------------------------

`route`  
_Type_: string, or list of strings  
_Desc_: The URL pattern to match in order for this route to be selected. May be a single route or
a list of multiple routes. If any of the routes at matched, this route config will be used to
handle the request. Variables may be defined in the route using the `<myvariable>` syntax.
See [Flask documentation on routes](https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing)
for more information. Variables defined in the route will be available for use by data _processors_
and templates inside the variable name `view_args`, e.g. `view_args.myvariable`.  

`template` (optional; mutually exclusive with `stream`)  
_Type_: string  
_Desc_: The name of the Jinja2 template file to attempt to render. The results of all defined data
_processors_ will be passed to this template. The result of this template will be rendered out
to the user. Jinja is a very powerful templating engine; for more info see the official
[Jinja2 documentation](https://jinja.palletsprojects.com/en/2.11.x/).  

`stream` (optional; mutually exclusive with `template`)  
_Type_: string  
_Desc_: The name of the data _processor_ to return as a stream of data. This stream is returned
as it is read, allowing it to handle extremely large sets of data or files without running up
against memory issues. A data _processor_ with a name matching this must be defined in the
`data` section.  

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
* `?` (all other arguments): Dependent on the _processor_; refer to that specific _processor_ documentation for details.  


