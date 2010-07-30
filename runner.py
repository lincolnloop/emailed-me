#!/usr/bin/python
"""Wrapper to setup our Python path and kickstart the application"""
import os
import sys

# add lib to our PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from wsgiref.handlers import CGIHandler
from application import app
CGIHandler().run(app)
