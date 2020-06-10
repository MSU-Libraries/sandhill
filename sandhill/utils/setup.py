import os
import logging
from flask import Flask
from .. import app

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass
    #TODO if we include a default config, won't the instance dir always exist?

app.config.from_pyfile(os.path.join(app.instance_path,'sandhill.default_settings.cfg'))

# If a instance specific config exists, load it
if os.path.exists(os.path.join(app.instance_path,"sandhill.cfg")):
    app.config.from_pyfile('sandhill.cfg')

# load the secret key 
app.secret_key =  app.config["SECRET_KEY"]

# configure logging
#TODO consider global logging vs app.logger logging
logging.basicConfig(filename=app.config["LOG_FILE"],
    level=app.config["LOG_LEVEL"],
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

