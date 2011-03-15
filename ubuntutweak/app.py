#!/usr/bin/python

# Ubuntu Tweak - Ubuntu Configuration Tool
#
# Copyright (C) 2007-2011 Tualatrix Chou <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

from gi.repository import Gtk, Unique

class MainWindow(Gtk.Window):
    pass


class App(Unique.App):
    def __init__(self, name='com.ubuntu-tweak.main', startup_id=''):
        Unique.App.__init__(self, name=name, startup_id=startup_id)

        self.connect('message-received', self.on_message_received)

    def set_main_window(self, window):
        self._window = window

    def on_message_received(self, app, command, message, time):
        if command == Unique.Command.ACTIVATE:
            self._window.present()

        return False
