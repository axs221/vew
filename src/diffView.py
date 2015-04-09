#!/usr/bin/python
import urwid
import subprocess
import re
from gitView import GitView

class DiffView(GitView):

    def __init__(self, parameters_manager, view_manager, first_commit, second_commit):
        self.parameters_manager = parameters_manager
        self.first_commit = first_commit
        self.second_commit = second_commit
        log = self.get()
        content = urwid.SimpleListWalker(log)

        self.content = content
        super(DiffView, self).__init__(parameters_manager, view_manager, content)

    def get(self):
        command = self.build_command()

        diff = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
        lines = diff.split('\n')
        return [ self.decorate(line) for line in lines ]

    def build_command(self):
        filename = self.parameters_manager.filename  # Note that filename may be empty

        command = "git diff " + self.first_commit
        if self.second_commit:
            command += ".." + self.second_commit
        command += " " + filename

        return command

    def decorate(self, text):
        line = urwid.Text(text)
        new_map = lambda attr: urwid.AttrMap(line, attr, 'reveal focus')
        if (re.match('^-', text)):
            return new_map('deleted')
        elif (re.match('^\+', text)):
            return new_map('added')
        elif (re.match('^diff', text)):
            return new_map('diff')
        return new_map('normal')

    def on_keypress(self, input):
        if input == 'q':
            self.view_manager.close_current_view()
        else:
            super(DiffView, self).on_keypress(input)
