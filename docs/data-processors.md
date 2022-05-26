# Sandhill Data Processors
Sandhill routes are composed of a list of **data processors**. These are single
actions that Sandhill may take while processing a request.

Things data processors can do:

* Gathering data by querying an API
* Loading configuration from a file
* Transforming or manipulating data
* Performing some evaluation or computation

If the data processors provided with Sandhill are not sufficient, you can [develop
your own data processor](#developing-a-data-processor) as well.

## Data Processors Included With Sandhill
* [evaluate](#)
* [file](#sandhill.processor.file) - Find and load files from the instance.
* [iiif](#)
* [request](#)
* [solr](#sandhill.processors.solr) - Calls to a Solr endpoint.
* [stream](#)
* [string](#)
* [template](#)
* [xml](#)


### Common Data Processor Arguments
These arguments are valid to pass to all data processors. Data processors **should** be written
to handle these arguments appropriately.  

#### `name` - _Required_  
Defines the label under which the data processor will run. Results from the processor will be
stored under this key in the data passed to subsequent processors.  

#### `processor` - _Required_  
Specifies the processor and method to call within the processor, period delimited.
```json
{
    "name": "searchresults",
    "processor": "solr.search"
}
```

#### `on_fail` - _Optional_  
Unless specified, the data processor is allowed to fail silently and proceed onto the next processor.  
When specified, the value must be the integer of a valid
[4xx or 5xx HTTP Status Code](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes) or `0`.
If the data processor fails and `on_fail` set, Sandhill will abort the page request and return an error
page with the selected code. If set to `0`, the processor may choose to return an appropriate code to
the type of failure.  

#### `when` - _Optional_  
A [Jinja rendered](#TODO) string which is then [evaluated for truth](https://docs.python.org/3/library/stdtypes.html#truth).
If the value is not truthy, then the given data processor will be skipped.  


::: sandhill.processors.evaluate

::: sandhill.processors.file

::: sandhill.processors.iiif

::: sandhill.processors.request

::: sandhill.processors.solr

::: sandhill.processors.stream

::: sandhill.processors.string

::: sandhill.processors.template

::: sandhill.processors.xml


## Developing a Data Processor
Sandhill makes developing your own data processors quite easy, perhaps best explained
with a simple example.  

### Simple Processor
Within your `instance/` ensure there is `processors/` sub-directory. If not create it.

Next create a new Python file in `instance/processors/`; we'll call our example file
`myproc.py`. Next up, we create a function in that file which accepts a single
parameter `data`.
```python
# instance/processors/myproc.py
"""The myproc data processors"""

def shout(data):
    """The shout data processor; will upper case all text and add an exlcaimation point."""
    ...
```

The `data` here is a dict containing all loaded data from a route up until this point.
If previous data processors loaded anything, it will be present in `data`. Also, all
keys arguments set for this data processor call will also be in `data`.

For our `shout()` processor, let's say we want to expect a key `words`, which will
contain the data we want to transform with our processor.

```python
def shout(data):
    """The shout data processor; will upper case all text and add an exlcaimation point."""
    return data["words"].upper() + "!"
```

That's mostly it! Now we could include our custom data processor in a route with this entry
in our route's JSON `data` list:
```json
{
    "name": "loudly",
    "processor": "myproc.shout",
    "words": "This is my statement"
}
```

And after the data processor runs, Sandhill will have the following in your route's `data` dict:
```
{
    "data": {
        ... # other route data as may be appropriate
        "loudly": "THIS IS MY STATEMENT!"
    }
}
```

### Improving your Processor
But what if someone fails to pass in the `words` key? Right now that would result in a `KeyError`.

In Sandhill, best practice for data processors is to return `None` on most failures. That is, unless
the `on_fail` key is set in `data`. In this case, we ought to abort with the value of `on_fail`.

To assist with this, Sandhill provide the `dp_abort()` function (short for data processor abort) which
will do most of the heavy lifting for you. Let's rework our method to handle failures..

```python
from sandhill.utils.error_handling import dp_abort

def shout(data):
    """The shout data processor; will upper case all text and add an exlcaimation point."""
    if "words" not in data:
        dp_abort(500)   # Here we choose HTTP status 500 for default, but `on_fail` value will take precedence.
        return None     # Always return None on a failure; if no `on_fail` is set, then we must return.
    return data["words"].upper() + "!"
```

With that, you have a nicely functioning data processor! For more advanced examples, feel free to peek
at the source code of the built-in Sandhill data processors above.
