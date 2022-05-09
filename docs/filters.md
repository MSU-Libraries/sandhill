# Template Filters in Sandhill
Sandhill makes extensive use of the [Jinja2 templating engine](https://jinja.palletsprojects.com/en/3.0.x/templates/)
as included with Flask. Jinja expression are allowed in template files and many Sandhill config files.

In addition to filters available from Flask, and the ability to define your own filters, Sandhill provides
a number of additional filters ready for use, all of which are listed below.

* [Flask Built-in Filters](https://jinja.palletsprojects.com/en/3.0.x/templates/#builtin-filters)
* [Creating a Custom Filter](#creating-a-custom-filter)
* **Sandhill Provided Filters**
    - [General Purpose Filters](#general-purpose-filters)
    - [Encoding/Formatting Filters](#encodingformatting-filters)
    - [Solr Filters](#solr-filters)
    - [Specialty Filters](#specialty-filters)

## Creating a Custom Filter
Sandhill has an easy way to integrate your own instance specific filters. Define your custom filters
and save them in `instance/filters/`. Sandhill will automatically load all files placed there and
any filtered defined will be available to your instance next time it's restarted.

To created a custom filter is no different than any other filter in Sandhill. Lets create an
example filter to ensure an exlaimation point is at the end of a string.

First we'll create a file to put it in: `instance/filters/myfilters.py`.

Then we can proceed to write our filter:
```python
from sandhill import app

@app.template_filter('exclaim')
def exclaim(value):
    """Returns the given value as a string, appending an exclamation mark if it
    doesn't already end with one."""
    value = str(value)
    if not value.endswith("!"):
        return f"{value}!"
    return value
```

That is all there is to it! The new filter is ready to use in Sandhll. Take a peek at the code
for other Sandhill filters if you'd like to see more examples.

## General Purpose Filters
::: sandhill.filters.filters.datepassed
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.deepcopy
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.getextension
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.head
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.islist
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.regex_match
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.regex_sub
    rendering:
      show_root_full_path: false
### `sandbug()`
::: sandhill.filters.filters.filter_sandbug
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
::: sandhill.filters.filters.setchildkey
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.todict
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.totuples
    rendering:
      show_root_full_path: false

## Encoding/Formatting Filters
::: sandhill.filters.filters.commafy
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.formatbinary
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.formatedate
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.unescape
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.urlquote
    rendering:
      show_root_full_path: false

## Solr Filters
::: sandhill.filters.filters.solr_addfq
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.solr_decode
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.solr_encode
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.solr_encodequery
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.solr_getfq
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.solr_hasfq
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.solr_removefq
    rendering:
      show_root_full_path: false

## Speciality Filters
::: sandhill.filters.filters.assembleurl
    rendering:
      show_root_full_path: false
### `getconfig()`
::: sandhill.filters.filters.filter_getconfig
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
::: sandhill.filters.filters.filtertags
### `xpath()`
::: sandhill.filters.filters.filter_xpath
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
### `xpath_by_id()`
::: sandhill.filters.filters.filter_xpath_by_id
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
::: sandhill.filters.filters.render
    rendering:
      show_root_full_path: false
::: sandhill.filters.filters.renderliteral
    rendering:
      show_root_full_path: false
