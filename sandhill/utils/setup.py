import os
import logging
import sys
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from importlib import import_module
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask.logging import create_logger
from sandhill import app
from sandhill.utils.generic import get_config
from jinja2 import ChoiceLoader, FileSystemLoader

def configure_logging():
    '''
    Configure application logging. Includes: default logger, file logger, 
    and email based on the application configuration file.
    '''

    # Default logger
    app.logger = create_logger(app)
    app.logger.setLevel(get_config('LOG_LEVEL', logging.WARNING))

    # File logger
    if get_config('LOG_FILE'):
        file_handler = RotatingFileHandler(get_config('LOG_FILE'), maxBytes=1024 * 1024 * 100, backupCount=5)
        file_handler.setLevel(get_config('LOG_LEVEL', logging.WARNING))
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(filename)s %(lineno)d]: %(message)s'
        ))
        app.logger.addHandler(file_handler)

    # Email logger
    if get_config('EMAIL'):
        email_log_level = logging.ERROR
        email_log_level = get_config('EMAIL_LOG_LEVEL', logging.ERROR)
        mail_handler = SMTPHandler(
            mailhost=get_config('EMAIL_HOST', '127.0.01'),
            fromaddr=get_config('EMAIL_FROM'),
            toaddrs=[get_config('EMAIL')],
            subject=get_config('EMAIL_SUBJECT', 'Sandhill Error')
        )
        mail_handler.setLevel(email_log_level)
        mail_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(filename)s %(lineno)d\n%(message)s'
        ))
        app.logger.addHandler(mail_handler)

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
app.config.from_pyfile(os.path.join(app.root_path, 'sandhill.default_settings.cfg'))

# If a instance specific config exists, load it
if os.path.exists(os.path.join(app.instance_path, "sandhill.cfg")):
    app.config.from_pyfile('sandhill.cfg')

# load the secret key
app.secret_key = get_config("SECRET_KEY")

# Set debug mode
app.debug = bool(get_config("DEBUG","False"))
# Add debug toolbar if debug mode is on and not running code via pytest
if app.debug and not "pytest" in sys.modules:
    toolbar = DebugToolbarExtension(app)
    toolbar._success_codes.extend([400, 401, 403, 404, 500, 501])

# Configure logging
configure_logging()

# Load any included bootstrap modules (ex: scss)
bootstrap_path = os.path.join(app.instance_path, 'bootstrap')
if os.path.exists(bootstrap_path):
    for module in os.listdir(bootstrap_path):
        if not module.endswith(".py"):
            continue
        try:
            mod = import_module(os.path.join(bootstrap_path, module).replace("/","."))
            mod()
        except Exception as exc:
            app.logger.error(f"Exception attempting to run bootstrap module '{module}' "
                               f"Error: {exc}")
            raise exc
