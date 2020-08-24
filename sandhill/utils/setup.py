import os
import logging
from flask import Flask
from sandhill import app
from jinja2 import ChoiceLoader, FileSystemLoader

# Ability to load templates from instance/templates/ directory
loader = ChoiceLoader([
    FileSystemLoader(os.path.join(app.instance_path, "templates/")),
    app.jinja_loader
])
app.jinja_loader = loader

# So we can load 'static' files from the instance/static/ directory
for rule in app.url_map.iter_rules('static'):
    # Remove the default rule as our static files are handled in routes/main.py
    app.url_map._rules.remove(rule)

# Set default config file
app.config.from_pyfile(os.path.join(app.instance_path, 'sandhill.default_settings.cfg'))

# If a instance specific config exists, load it
if os.path.exists(os.path.join(app.instance_path, "sandhill.cfg")):
    app.config.from_pyfile('sandhill.cfg')

# load the secret key 
app.secret_key =  app.config["SECRET_KEY"]

# Set log level
# TODO make this a parameter
app.logger.setLevel(logging.DEBUG) 
