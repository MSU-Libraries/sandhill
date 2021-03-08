"""
Config file executed before pytest runs tests
"""
import os
import sys
from flask import Flask
from importlib import import_module
cur_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, cur_path)
if "INSTANCE_DIR" not in os.environ or not os.environ["INSTANCE_DIR"]:
    os.environ["INSTANCE_DIR"] = os.path.join(cur_path, "sandhill/test_instance")

def pytest_unconfigure(config):
    mod = import_module('sandhill.utils.generic')
    logpath = mod.get_config('LOG_FILE')
    if os.path.exists(logpath):
        os.unlink(logpath)
