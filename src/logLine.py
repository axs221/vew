#!/usr/bin/python

class LogLine(object):

    def __init__(self, text, commit):
        self.text = text
        self.commit = commit

    def __str__(self):
        return self.text
