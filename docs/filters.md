# Template Filters in Sandhill
Sandhill makes extensive use of the [Jinja2 templating engine](https://jinja.palletsprojects.com/en/3.0.x/templates/)
as included with Flask. Jinja expression are allowed in template files and many Sandhill config files.

The complete [list of built-in filters](#https://jinja.palletsprojects.com/en/3.0.x/templates/#builtin-filters) 
available with Flask are also available in Sandhill. In addition, Sandhill provides a number of additional filters
for use, which are [listed below](#general-purpose-filters).

## Creating a Filter
Sandhill has an easy way to integrate your own instance specific filters.
```
TODO
```

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
