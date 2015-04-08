#!/usr/bin/python
import sys
import urwid
import subprocess
import re
from Queue import LifoQueue

class ViewManager(object):
    def __init__(self):
        self.main_frame = None
        self.current_view = None
        self.last_view_stack = LifoQueue()

    def start(self):
        self._loop = urwid.MainLoop(self.main_frame, self.get_pallette(), unhandled_input=self.on_keypress)
        self._loop.run()

    def change_view(self, view):
        self.last_view_stack.put(self.current_view)
        self._update_view(view)

    def close_current_view(self):
        view = self.last_view_stack.get()
        self._update_view(view)

    def _update_view(self, view):
        self.current_view = view
        self.main_frame.contents['body'] = ( view, None )
        self._loop.draw_screen()

    def on_keypress(self, input):
        self.current_view.on_keypress(input)

    def get_pallette(self):
        palette = [('header', 'black', 'dark green', 'standout'),
                   ('normal', 'white', 'black'),
                   ('reveal focus', 'white', 'dark blue', 'standout'),
                   ('diff', 'black', 'dark green', 'standout'),
                   ('added', 'dark green', 'black'),
                   ('deleted', 'dark red', 'black')]
        return palette

class ParametersManager(object):
    def __init__(self):
        self.filename = ""
        if len(sys.argv) > 1:
            self.filename = sys.argv[1]

class App(object):

    def run_app(self):
        self.init_parameters_manager()
        self.init_view_manager()

        self.view_manager.start()

    def init_parameters_manager(self):
        self.parameters_manager = ParametersManager()

    def init_view_manager(self):
        self.view_manager = ViewManager()
        view = LogView(self.parameters_manager, self.view_manager)
        view.show_key = urwid.Text("Press any key", wrap='clip')
        self.view_manager.current_view = view

        head = urwid.AttrMap(view.show_key, 'header')
        self.view_manager.main_frame = urwid.Frame(view, head, focus_part='body')


class GitView(urwid.ListBox):

    def __init__(self, parameters_manager, view_manager, content):
        self.parameters_manager = parameters_manager
        self.view_manager = view_manager
        super(GitView, self).__init__(content)

    def on_keypress(self, input):
        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif input in [ 'up', 'k' ]:
            self.move_up()
        elif input in [ 'down', 'j' ]:
            self.move_down()

    def move_down(self):
        focus_widget, idx = super(GitView, self).get_focus()
        if idx < len(self.content) - 1:
            idx = idx + 1
            self.set_focus(idx)

    def move_up(self):
        focus_widget, idx = super(GitView, self).get_focus()
        if idx > 0:
            idx = idx - 1
            self.set_focus(idx)

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


class LogLine(object):

    def __init__(self, text, commit):
        self.text = text
        self.commit = commit

    def __str__(self):
        return self.text

class LogView(GitView):

    def __init__(self, parameters_manager, view_manager):
        self.parameters_manager = parameters_manager

        log = self.get()

        content = urwid.SimpleListWalker(log)
        self.content = content

        self.selected_commit = None

        super(LogView, self).__init__(parameters_manager, view_manager, content)

    def out(self, s):
        self.show_key.set_text(str(s))

    def get(self):
        filename = self.parameters_manager.filename  # Note that filename may be empty
        log = subprocess.Popen(
            "git log " + filename
            , shell=True, stdout=subprocess.PIPE).stdout.read()
        lines = log.split('\n')
        builder = LogLinesBuilder()
        [ builder.add_line(line) for line in lines ]
        return builder.build()

    def on_keypress(self, input):
        if input == 'h':
            self.add_to_diff(input)
        if input == 'enter':
            self.add_to_diff(input)
        elif input == 'c':
            show_key = self.view_manager.current_view.show_key
            self.selected_commit = None
            show_key.set_text("Press any key")
        else:
            super(LogView, self).on_keypress(input)

    def add_to_diff(self, input):
        if self.selected_commit or input == 'h':
            listbox = None

            if input == 'h':
                previously_selected_commit = 'HEAD'
                newly_selected_commit = None
            else:
                previously_selected_commit = self.selected_commit
                newly_selected_commit = self.content[self.focus_position].commit

            self.show_diff(previously_selected_commit, newly_selected_commit)
        else: 
            show_key = self.view_manager.current_view.show_key
            self.selected_commit = self.content[self.focus_position].commit
            show_key.set_text("Press enter on another commit, or enter here again to compare to HEAD\nCommit: " + self.selected_commit)

    def show_diff(self, before_commit, after_commit):
        if before_commit == after_commit:
            listbox = DiffView(self.parameters_manager, self.view_manager, after_commit, 'HEAD')
        else:
            listbox = DiffView(self.parameters_manager, self.view_manager, before_commit, after_commit)

        self.view_manager.change_view(listbox)

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


if __name__ == '__main__':
    app = App()
    app.run_app()
