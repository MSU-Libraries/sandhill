"""
Config file executed before pytest runs tests
"""
import os
import sys
from dotenv import load_dotenv
from flask import Flask
from importlib import import_module
cur_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, cur_path)
load_dotenv('/etc/environment')
load_dotenv()
if "INSTANCE_DIR" not in os.environ or not os.environ["INSTANCE_DIR"]:
    os.environ["INSTANCE_DIR"] = os.path.join(cur_path, "tests/instance")

def pytest_configure(config):
    from sandhill import app
    mod = import_module('sandhill.utils.generic')
    app.config['SERVER_NAME'] = mod.getconfig('SERVER_NAME')

def pytest_unconfigure(config):
    mod = import_module('sandhill.utils.generic')
    logpath = mod.getconfig('LOG_FILE')
    if os.path.exists(logpath):
        os.unlink(logpath)
