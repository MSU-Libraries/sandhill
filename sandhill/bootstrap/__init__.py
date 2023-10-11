'''
Application setup utilities
'''
import builtins
import os
import logging
import sys
import string
import secrets
from importlib import import_module
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask.logging import create_logger
from jinja2 import ChoiceLoader, FileSystemLoader, select_autoescape
from sandhill import app
from sandhill.utils.generic import getconfig, getmodulepath

def configure_logging():
    '''
    Configure application logging. Includes: default logger, file logger,
    and email based on the application configuration file.
    '''

    # Default logger
    app.logger = create_logger(app)
    app.logger.setLevel(getconfig('LOG_LEVEL', logging.WARNING))

    # File logger
    if getconfig('LOG_FILE'):
        file_handler = RotatingFileHandler(
            getconfig('LOG_FILE'), maxBytes=1024 * 1024 * 100, backupCount=5
        )
        file_handler.setLevel(getconfig('LOG_LEVEL', logging.WARNING))
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(filename)s %(lineno)d]: %(message)s'
        ))
        app.logger.addHandler(file_handler)

    # Email logger
    if getconfig('EMAIL'):
        email_log_level = getconfig('EMAIL_LOG_LEVEL', logging.ERROR)
        mail_handler = SMTPHandler(
            mailhost=getconfig('EMAIL_HOST', '127.0.0.1'),
            fromaddr=getconfig('EMAIL_FROM'),
            toaddrs=[getconfig('EMAIL')],
            subject=getconfig('EMAIL_SUBJECT', 'Sandhill Error')
        )
        mail_handler.setLevel(email_log_level)
        mail_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(filename)s %(lineno)d\n%(message)s'
        ))
        app.logger.addHandler(mail_handler)

# Set which files are autoescaped when rendering
app.jinja_options = {
    "autoescape": select_autoescape([".html", ".htm", ".xml", ".xhtml", ".html.j2"])
}

# Ability to load templates from instance/templates/ directory
loader = ChoiceLoader([
    FileSystemLoader(os.path.join(app.instance_path, "templates/")),
    app.jinja_loader
])
app.jinja_loader = loader

# So we can load 'static' files from the instance/static/ directory, we
# wemove the default rule; our static files are handled in routes/static.py
app.url_map._rules_by_endpoint.pop('static', None) # pylint: disable=protected-access
app.url_map._matcher._root.static = {} # pylint: disable=protected-access
app.view_functions.pop('static', None)

# Set default config file
app.config.from_pyfile(os.path.join(app.root_path, 'sandhill.default_settings.cfg'))

# If a instance specific config exists, load it
if os.path.exists(os.path.join(app.instance_path, "sandhill.cfg")):
    app.config.from_pyfile('sandhill.cfg')

# Load the secret key
SECRET_KEY = "".join(secrets.SystemRandom().choice(
    string.ascii_letters + string.digits) for _ in range(64))
app.config["SECRET_KEY"] = getconfig("SECRET_KEY", SECRET_KEY)

# Nicer JSON output
app.json.compact = False

# Set debug mode
app.debug = bool(int(getconfig("DEBUG", "0")))

# Configure logging
configure_logging()

def sandbug(value, comment=None):
    """
    Shortcut to debug a variable and its type
    """
    comment = f" ({comment})" if comment else ""
    app.logger.debug(f"SANDBUG{comment}: {value} TYPE: {type(value)}")
    return ""
builtins.sandbug = sandbug

def load_modules(base_path, sub_path, files=True, dirs=True, exclude=None):
    '''
    Detect and load all of the modules within a given path
    args:
        base_path(str): Base directory path to search
        sub_path(str): Directory within the base path to search
        files (bool): Include loading files. Default is True
        dirs (bool): Include loading directories. Default is True
        exclude (list of  str): Files and directories to exclude
    '''
    sub_path = sub_path.strip('/')
    mod_path = os.path.join(base_path, sub_path)
    if os.path.exists(mod_path):
        for module in os.scandir(mod_path):
            if (not files and module.is_file()) \
              or (not dirs and module.is_dir()):
                continue
            if module.is_file() and not module.name.endswith('.py') \
              or module.name in exclude:
                continue
            absolute_module = getmodulepath(os.path.join(base_path, sub_path, module.name))
            # Do not load modules if they are already loaded/loading
            if absolute_module not in sys.modules:
                try:
                    import_module(absolute_module)
                except Exception as exc:
                    app.logger.error(
                        f"Exception attempting to load module '{absolute_module}' in {base_path} "
                        f"Error: {exc}"
                    )
                    raise exc

load_modules(app.root_path, 'bootstrap', exclude=['__pycache__', '__init__.py'])
load_modules(app.instance_path, 'bootstrap', exclude=['__pycache__', '__init__.py'])
load_modules(app.root_path, 'commands', exclude=['__pycache__', '__init__.py'])
load_modules(app.instance_path, 'commands', exclude=['__pycache__', '__init__.py'])
load_modules(app.root_path, 'filters', exclude=['__pycache__', '__init__.py'])
load_modules(app.instance_path, 'filters', exclude=['__pycache__', '__init__.py'])
load_modules(app.root_path, 'context', exclude=['__pycache__', '__init__.py'])
load_modules(app.root_path, 'utils/context', exclude=['__pycache__', '__init__.py'])
load_modules(app.instance_path, 'context', exclude=['__pycache__', '__init__.py'])
