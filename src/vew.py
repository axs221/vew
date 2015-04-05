#!/usr/bin/python
import urwid
import subprocess
import re

class App(object):

    def run_app(self):

        items = [urwid.Text("foo"),
                urwid.Text("bar"),
                urwid.Text("baz")]

        log = self.get_log()
        content = urwid.SimpleListWalker(log)

        listbox = LogView(content)

        listbox.show_key = urwid.Text("Press any key", wrap='clip')
        head = urwid.AttrMap(listbox.show_key, 'header')
        top = urwid.Frame(listbox, head)

        loop = urwid.MainLoop(top, self.get_pallette(), input_filter=listbox.show_all_input,
                                unhandled_input=listbox.on_keypress)
        loop.run()

        top.set_body(urwid.Text("HAHA YOU HAVE BEEN H4cKed"))
        loop.draw_screen()

    def get_log(self):
        log = GitLog()
        response = log.get()
        return response

    def get_diff(self):
        diff = GitDiff()
        response = diff.get()
        return response

    def get_pallette(self):
        palette = [('header', 'white', 'white', 'standout'),
                   ('normal', 'white', 'black'),
                   ('reveal focus', 'white', 'dark blue', 'standout'),
                   ('diff', 'black', 'dark green', 'standout'),
                   ('added', 'dark green', 'black'),
                   ('deleted', 'dark red', 'black')]
        return palette

class LogView(urwid.ListBox):

    def __init__(self, content):
        self.content = content
        super(LogView, self).__init__(content)

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
        focus_widget, idx = super(LogView, self).get_focus()
        if idx < len(self.content) - 1:
            idx = idx + 1
            self.set_focus(idx)

    def move_up(self):
        focus_widget, idx = super(LogView, self).get_focus()
        if idx > 0:
            idx = idx - 1
            self.set_focus(idx)

    def out(self, s):
        self.show_key.set_text(str(s))

class GitLog(object):

    def get(self):
        log = subprocess.Popen(
            "git log"
            , shell=True, stdout=subprocess.PIPE).stdout.read()
        lines = log.split('\n')
        return [ self.decorate(line) for line in lines ]

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

class GitDiff(object):
    def get(self):
        diff = subprocess.Popen(
            "git diff HEAD^^..HEAD"
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
