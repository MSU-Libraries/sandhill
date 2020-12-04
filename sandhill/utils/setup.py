import os
import sass
import logging
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask.logging import create_logger
from sandhill import app
from sandhill.commands.compile_scss import run_compile
from jinja2 import ChoiceLoader, FileSystemLoader
from sassutils.wsgi import SassMiddleware

# Ability to load templates from instance/templates/ directory
loader = ChoiceLoader([
    FileSystemLoader(os.path.join(app.instance_path, "templates/")),
    app.jinja_loader
])
app.jinja_loader = loader

# So we can load 'static' files from the instance/static/ directory
for rule in app.url_map.iter_rules('static'):
    # Remove the default rule as our static files are handled in routes/static.py
    app.url_map._rules.remove(rule)

# Set default config file
app.config.from_pyfile(os.path.join(app.instance_path, 'sandhill.default_settings.cfg'))

# If a instance specific config exists, load it
if os.path.exists(os.path.join(app.instance_path, "sandhill.cfg")):
    app.config.from_pyfile('sandhill.cfg')

# load the secret key 
app.secret_key = app.config["SECRET_KEY"]

# set debug mode
app.debug = bool(app.config["DEBUG"])
if app.debug:
    toolbar = DebugToolbarExtension(app)
    toolbar._success_codes.extend([400, 401, 403, 404, 500, 501])


# Set log level
app.logger = create_logger(app)
if app.debug:
    app.logger.setLevel(logging.DEBUG)
else:
    app.logger.setLevel(logging.WARN)

# Add Sass middleware. This should help us complie CSS from Sass
if 'COMPILE_SCSS_ON_REQUEST' in app.config and bool(app.config['COMPILE_SCSS_ON_REQUEST']):
    app.wsgi_app = SassMiddleware(
        app.wsgi_app,
        {
            'instance': {
                'sass_path': 'static/scss',
                'css_path': 'static/css/compiled',
                'wsgi_path': 'static/css/compiled',
                'strip_extension': True
            }
        },
        {
            'instance': app.instance_path
        }
    )
else:
    # If we're not in debug mode, we don't need the scss recompiled each page load,
    # so we just load it when the application is started.
    # If this starts taking too long, we can move it to docker build or CI/CD
    try:
        run_compile()
    except Exception as exc:
        app.logger.error(f"Error compiling scss: {exc}")
