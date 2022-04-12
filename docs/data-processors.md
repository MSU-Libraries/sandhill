# Sandhill Data Processors
Sandhill routes are composed of a list of **data processors**. These are single
actions that Sandhill may take while processing a request.

Things data processors can do:

* Gathering data by querying an API
* Loading configuration from a file
* Transforming or manipulating data
* Performing some evaluation or computation

If the data processors provided with Sandhill are not sufficient, you can develop
your [own data processor](#developing-a-data-processor) as well.

## Data Processors Included With Sandhill
* [file](#sandhill.processor.file) - Find and load files from the instance.
* [solr](#sandhill.processors.solr) - Calls to a Solr endpoint.

### Common Data Processor Arguments
These arguments are valid to pass to all data processors. Data processors **should** be written
to handle these arguments appropriately.  

#### `name` _Required_  
Defines the label under which the data processor will run. Results from the processor will be
stored under this key in the data passed to subsequent processors.  

#### `processor` _Required_  
Specifies the processor and method to call within the processor, period delimited.
```json
{
    "name": "searchresults",
    "processor": "solr.search"
}
```

#### `on_fail` _Optional_  
Unless specified, the data processor is allowed to fail silently and proceed onto the next processor.  
When specified, the value must be the integer of a valid
[4xx or 5xx HTTP Status Code](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes) or `0`.
If the data processor fails and `on_fail` set, Sandhill will abort the page request and return an error
page with the selected code. If set to `0`, the processor may choose to return an appropriate code to
the type of failure.  

#### `when` _Optional_  
A [Jinja rendered](#TODO) string which is then [evaluated for truth](https://docs.python.org/3/library/stdtypes.html#truth).
If the value is not truthy, then the given data processor will be skipped.  


::: sandhill.processors.file

::: sandhill.processors.solr

## Developing a Data Processor
TODO
