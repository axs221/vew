#!/usr/bin/python
import urwid
import re

class LogLinesBuilder(object):
    def __init__(self):
        self.lines = []
        self.current_commit = ''

    def add_line(self, text):
        self.parse_line(text)
        decorated = self.decorate(text)
        decorated.commit = self.current_commit
        self.lines.append(decorated)
        return self

    def parse_line(self, text):
        commit_match = re.match('^commit\s+(\w+)', text)
        if commit_match:
            self.current_commit = commit_match.group(1)

    def build(self):
        lines = self.lines
        self.lines = []
        return lines

    def decorate(self, text):
        line = urwid.Text(text)
        new_map = lambda attr: urwid.AttrMap(line, attr, 'reveal focus')
        if (re.match('^-', text)):
            return new_map('deleted')
        elif (re.match('^\+', text)):
            return new_map('added')
        elif (re.match('^log', text)):
            return new_map('log')
        return new_map('normal')
