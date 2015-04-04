#!/usr/bin/python
import urwid

class App(object):
    def run_app(self):

        items = [urwid.Text("foo"),
                urwid.Text("bar"),
                urwid.Text("baz")]

        content = urwid.SimpleListWalker([
            urwid.AttrMap(w, None, 'reveal focus') for w in items])

        listbox = LogView(content)

        listbox.show_key = urwid.Text("Press any key", wrap='clip')
        head = urwid.AttrMap(listbox.show_key, 'header')
        top = urwid.Frame(listbox, head)

        loop = urwid.MainLoop(top, self.get_pallette(), input_filter=listbox.show_all_input, 
                unhandled_input=listbox.exit_on_cr)
        loop.run()

    def get_pallette(self):
        palette = [('header', 'white', 'black'),
                  ('reveal focus', 'white', 'dark blue', 'standout')]
        return palette

class LogView(urwid.ListBox):
    def __init__(self, content):
        self.content = content
        super(LogView, self).__init__(content)

    def show_all_input(self, input, raw):

        self.show_key.set_text("Pressed: " + " ".join([
            unicode(i) for i in input]))
        return input

    def exit_on_cr(self, input):
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

if __name__ == '__main__':
    app = App()
    app.run_app()
