import os
import sass
import logging
import sys
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask.logging import create_logger
from sandhill import app
from sandhill.commands.compile_scss import run_compile
from sandhill.utils.generic import get_config
from jinja2 import ChoiceLoader, FileSystemLoader
from sassutils.wsgi import SassMiddleware

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
app.config.from_pyfile(os.path.join(app.instance_path, 'sandhill.default_settings.cfg'))

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

# Add Sass middleware. This should help us complie CSS from Sass
if bool(get_config('COMPILE_SCSS_ON_REQUEST','False')):
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
