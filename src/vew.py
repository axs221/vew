#!/usr/bin/python
import urwid
import subprocess
import re

class App(object):

    def run_app(self):

        items = [urwid.Text("foo"),
                urwid.Text("bar"),
                urwid.Text("baz")]

        listbox = LogView()
        listbox.show_key = urwid.Text("Press any key", wrap='clip')
        self.current_listbox = listbox

        head = urwid.AttrMap(listbox.show_key, 'header')
        self.top = urwid.Frame(listbox, head, focus_part='body')

        self.loop = urwid.MainLoop(self.top, self.get_pallette(), input_filter=listbox.show_all_input,
                                unhandled_input=self.on_keypress)
        self.loop.run()

    def on_keypress(self, input):
        if (input == 'enter'):
            listbox = DiffView(self.current_listbox.content[self.current_listbox.focus_position].commit)
            listbox.show_key = urwid.Text("Press any key", wrap='clip')
            self.current_listbox = listbox
            self.top.contents['body'] = ( listbox, None )
            self.loop.draw_screen()
        else:
            self.current_listbox.on_keypress(input)

    def gui_clear(self):
        self.loop.widget = urwid.Filler(urwid.Text(u''))
        self.loop.draw_screen()

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

class GitView(urwid.ListBox):

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
        self.current_commit = 'd843714290be3cdb50ba1d5c80da06971051bb09'

    def add_line(self, text):
        decorated = self.decorate(text)
        decorated.commit = self.current_commit
        self.lines.append(decorated)
        return self

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

    def __init__(self):
        log = self.get()
        content = urwid.SimpleListWalker(log)

        self.content = content
        super(LogView, self).__init__(content)


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

class DiffView(GitView):

    def __init__(self, commit):
        self.commit = commit
        log = self.get()
        content = urwid.SimpleListWalker(log)

        self.content = content
        super(DiffView, self).__init__(content)

    def get(self):
        diff = subprocess.Popen(
            "git diff " + self.commit + "..HEAD"
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
