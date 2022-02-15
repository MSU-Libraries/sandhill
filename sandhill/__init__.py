'''
Creates the Flask application and is the entry point for the application
'''
import os
from flask import Flask
install_dir = os.path.dirname(os.path.dirname(__file__))
app = Flask(__name__,
            instance_relative_config=True,
            instance_path=os.path.join(install_dir, os.environ["INSTANCE_DIR"])
            if "INSTANCE_DIR" in os.environ
            else None)
app.install_dir = install_dir
# Local imports requiring the Flask app
from sandhill.utils.error_handling import catch # pylint: disable=wrong-import-position
import sandhill.bootstrap # pylint: disable=wrong-import-position
from sandhill.routes import main, static, error # pylint: disable=wrong-import-position
