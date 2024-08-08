# Sandhill API Reference
This document provides API reference for Sandhill code not covered
by the user documentation. If you plan on developing
additional data processors, filters, or the like, this may be
useful. Otherwise, you can safely ignore these documentation pages.

## Routes
Core routing API should not be needed even when developing new
functionality for your instance. Still, it's provided here for
the curious.

::: sandhill.routes.static

::: sandhill.routes.error

::: sandhill.routes.main

## Data Processors
Sandhill routes are composed of a list of **data processors**. These are single
actions that Sandhill may take while processing a request. See the
[data processor](./data-processors.md) documentation for full details.

## Utils
Utilities are bits of helper code used elsewhere in Sandhill. Functions or
classes in `utils/` may be useful in writing instance specific code for your
Sandhill site.

::: sandhill.utils.api

::: sandhill.utils.config_loader

::: sandhill.utils.context

::: sandhill.utils.error_handling

::: sandhill.utils.generic

### `utils.html.HTMLTagFilter`
Class used to filter through HTML and remove all tags except for those set as allowed.
Used by the `filtertags()` template filter.

::: sandhill.utils.jsonpath
    options:
      members_order: "source"

::: sandhill.utils.request

### `utils.solr.Solr`
Class for handling Solr related logic, such as encoding/decoding.

::: sandhill.utils.template

::: sandhill.utils.test

::: sandhill.utils.xml


## Bootstrap
This is the code that starts up Sandhill, initializing the application.
Have a look at the [bootstrap](./bootstrap.md) documentation for more details.

### `bootstrap`
The core of the bootstrap module handles, among other things, loading other Python code.

### `bootstrap.request`
::: sandhill.bootstrap.request.update_request_object
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      show_source: false

### `bootstrap.g`
::: sandhill.bootstrap.g.g_set
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      show_source: false

### `bootstrap.debugtoolbar`
::: sandhill.bootstrap.debugtoolbar
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false

### `bootstrap.disable_debug_caching`
::: sandhill.bootstrap.disable_debug_caching.disable_browser_cache
    rendering:
      show_root_heading: false
      show_root_toc_entry: false
      show_root_full_path: false
      show_source: false
