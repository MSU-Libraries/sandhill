# Sandhill API Reference
This document provides a full API reference for Sandhill code not
covered by user-facing documentation. If you plan on developing
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
[data processor](/data-processors) documentation for more details.

::: sandhill.processors.file

::: sandhill.processors.solr
