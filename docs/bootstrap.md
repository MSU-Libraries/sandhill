# Sandhill's Bootstrap Process
The bootstrap process is how Sandhill initializes itself and starts
running, and is done before any requests are able to be served. This
whole process takes only a few seconds and runs automatically.


## Bootstrap Steps

1. The Flask application is created
2. Core bootstrap functionality initiated
    * Include `instance/` path for templates and static path routes
    * Load the `sandhill.cfg` config file
    * Configure logging
3. Load code from both core Sandhill and the site instance (in that order for each item)
    * Bootstrap files in `bootstrap/`
    * Command files from `commands/`
    * Template filters from `filters/`
    * Context functionality from `context/`
4. Load routes from `instance/config/routes/`


## Adding Instance Bootstrap Code
Adding code specific to your instance into Sandhill is as simple
as placing your code into one of the appropriate directories:

- `instance/bootstrap/`
- `instance/commands/`
- `instance/filters/`
- `instance/context/`

There is technically no difference between the above directories other than the order
in which they are loaded. Any Python (`.py`) file located in the above directories
will be auto-loaded upon Sandhill's start.

Adding or editing a Python file located in the above _after_ Sandhill has started will
_not_ be loaded until Sandhill is restarted.


## Core Sandhill Bootstrap Files
If you're curious, have a look at the bootstrap source code of Sandhill over at
the [API reference](./api-reference.md#bootstrap) page.
