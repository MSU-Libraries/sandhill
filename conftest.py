"""
Config file executed before pytest runs tests
"""
import os
from flask import Flask
import sys
cur_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, cur_path)
if "TEST_INSTANCE_DIR" not in os.environ or not os.environ["TEST_INSTANCE_DIR"]:
    os.environ["TEST_INSTANCE_DIR"] = os.path.join(cur_path, "sandhill/test_instance/")
