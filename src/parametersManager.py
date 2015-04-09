#!/usr/bin/python
import sys

class ParametersManager(object):
    def __init__(self):
        self.filename = ""
        if len(sys.argv) > 1:
            self.filename = sys.argv[1]
