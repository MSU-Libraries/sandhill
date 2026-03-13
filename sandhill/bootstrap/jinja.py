'''
Jinja bootstrap
'''
from sandhill import app

# Remove exta whitespace from page templates
# to reduce page size
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Enable zip filter
app.jinja_env.globals.update(zip=zip)
