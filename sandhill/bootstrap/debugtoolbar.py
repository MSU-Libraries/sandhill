'''
Bootstrap hook to add FlaskDebugToolbar to the Flaks application when debug mode is enabled.
'''
import sys
from flask_debugtoolbar import DebugToolbarExtension
from sandhill import app

# Add debug toolbar if debug mode is on and not running code via pytest
if app.debug and "pytest" not in sys.modules:
    toolbar = DebugToolbarExtension(app)
