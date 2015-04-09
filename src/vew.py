#!/usr/bin/python
import urwid
from logView import LogView
from parametersManager import ParametersManager
from viewManager import ViewManager

class Vew(object):

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

if __name__ == '__main__':
    vew = Vew()
    vew.run_app()
