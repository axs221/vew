#!/usr/bin/python
import urwid
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
