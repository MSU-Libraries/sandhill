import os
import logging
from flask import Flask
from .. import app

app.config.from_pyfile(os.path.join(app.instance_path,'sandhill.default_settings.cfg'))

# If a instance specific config exists, load it
if os.path.exists(os.path.join(app.instance_path,"sandhill.cfg")):
    app.config.from_pyfile('sandhill.cfg')

# load the secret key 
app.secret_key =  app.config["SECRET_KEY"]
