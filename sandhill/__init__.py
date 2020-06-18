import os
from flask import Flask
install_dir = os.path.dirname(os.path.dirname(__file__))
app = Flask(__name__, instance_relative_config=True)
# Local imports requiring the Flask app
from .utils import setup, filters
from .routes import main

if __name__ == "__main__":
    app.run(debug=True)
