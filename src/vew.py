#!/usr/bin/python
import urwid
import subprocess
import re
from Queue import LifoQueue

class ViewManager(object):
    def __init__(self):
        self.main_frame = None
        self.current_view = None

    def start(self):
        self._loop = urwid.MainLoop(self.main_frame, self.get_pallette(), input_filter=self.current_view.show_all_input,
                                unhandled_input=self.on_keypress)
        self._loop.run()

    def change_view(self, view):
        self.current_view = view
        self.main_frame.contents['body'] = ( view, None )
        self._loop.draw_screen()

    def on_keypress(self, input):
        self.current_view.on_keypress(input)

    def get_pallette(self):
        palette = [('header', 'white', 'white', 'standout'),
                   ('normal', 'white', 'black'),
                   ('reveal focus', 'white', 'dark blue', 'standout'),
                   ('diff', 'black', 'dark green', 'standout'),
                   ('added', 'dark green', 'black'),
                   ('deleted', 'dark red', 'black')]
        return palette

class App(object):

    def run_app(self):

        items = [urwid.Text("foo"),
                urwid.Text("bar"),
                urwid.Text("baz")]

        self.view_manager = ViewManager()
        view = LogView(self.view_manager)
        view.show_key = urwid.Text("Press any key", wrap='clip')
        self.view_manager.current_view = view

        head = urwid.AttrMap(view.show_key, 'header')
        self.view_manager.main_frame = urwid.Frame(view, head, focus_part='body')

        self.view_manager.start()


class ViewController(object):
    def __init__(self):
        self.current_listbox = None
        self.last_listbox_stack = LifoQueue()

class GitView(urwid.ListBox):

    def __init__(self, view_manager, content):
        self.view_manager = view_manager
        super(GitView, self).__init__(content)

    def show_all_input(self, input, raw):
        self.show_key.set_text("Pressed: " + " ".join([
            unicode(i) for i in input]))
        return input

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

    def __init__(self, view_manager):
        log = self.get()

        content = urwid.SimpleListWalker(log)
        self.content = content

        self.selected_commit = None

        super(LogView, self).__init__(view_manager, content)

    def out(self, s):
        self.show_key.set_text(str(s))

    def get(self):
        log = subprocess.Popen(
            "git log"
            , shell=True, stdout=subprocess.PIPE).stdout.read()
        lines = log.split('\n')
        builder = LogLinesBuilder()
        [ builder.add_line(line) for line in lines ]
        return builder.build()

    def on_keypress(self, input):
        if input == 'enter':
            if self.selected_commit:
                listbox = None
                previously_selected_commit = self.selected_commit
                newly_selected_commit = self.content[self.focus_position].commit
                if previously_selected_commit == newly_selected_commit:
                    listbox = DiffView(self.view_manager, newly_selected_commit, 'HEAD')
                else:
                    listbox = DiffView(self.view_manager, previously_selected_commit, newly_selected_commit)

                self.view_manager.change_view(listbox)
            else: 
                show_key = self.view_manager.current_view.show_key
                self.selected_commit = self.content[self.focus_position].commit
                show_key.set_text("Press enter on another commit, or enter here again to compare to HEAD\nCommit: " + self.selected_commit)
        else:
            super(LogView, self).on_keypress(input)

class DiffView(GitView):

    def __init__(self, view_manager, first_commit, second_commit):
        self.first_commit = first_commit
        self.second_commit = second_commit
        log = self.get()
        content = urwid.SimpleListWalker(log)

        self.content = content
        super(DiffView, self).__init__(view_manager, content)

    def get(self):
        diff = subprocess.Popen(
            "git diff " + self.first_commit + ".." + self.second_commit
            , shell=True, stdout=subprocess.PIPE).stdout.read()
        lines = diff.split('\n')
        return [ self.decorate(line) for line in lines ]

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
       

if __name__ == '__main__':
    app = App()
    app.run_app()
