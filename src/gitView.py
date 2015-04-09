#!/usr/bin/python
import urwid

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
