'''
Creates the Flask application and is the entry point for the application
'''
import os
from flask import Flask
install_dir = os.path.dirname(os.path.dirname(__file__))
app = Flask(__name__, instance_relative_config=True)

# Local imports requiring the Flask app
from sandhill.utils import setup, filters # pylint: disable=wrong-import-position
from sandhill.routes import main, static, error # pylint: disable=wrong-import-position
from sandhill.commands import compile_scss # pylint: disable=wrong-import-position
