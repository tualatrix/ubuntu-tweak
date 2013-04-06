#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configuration tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
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

import os
import sys
import inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gi.repository import Gtk, Gdk

from ubuntutweak.common.debug import enable_debugging

class Test:
    def __init__(self, model):
        win = Gtk.Window()
        win.connect('destroy', lambda *w: Gtk.main_quit())
        win.set_position(Gtk.WindowPosition.CENTER)
        win.set_default_size(640, 400)

        if getattr(model, "__name__", None):
            win.set_title(model.__name__)
        else:
            win.set_title(str(model))

        if callable(model):
            win.add(model())
        else:
            win.add(model)
        win.show_all()

        Gtk.main()

class ManyTest:
    def __init__(self, widgets):
        win = Gtk.Window()

        win.connect('destroy', lambda *w: Gtk.main_quit())
        win.set_position(Gtk.WindowPosition.CENTER)

        win.set_title("Many test")
        
        vbox = Gtk.VBox(False, 10)
        win.add(vbox)

        for widget in widgets:
            vbox.pack_start(widget, False, False, 5)

        win.show_all()

        Gtk.main()

if __name__ == '__main__':
    enable_debugging()

    module = os.path.splitext(os.path.basename(sys.argv[1]))[0]
    folder = os.path.dirname(sys.argv[1])
    package = __import__('.'.join([folder, module]))

    for k, v in inspect.getmembers(getattr(package, module)):
        if k not in ('TweakModule', 'proxy') and hasattr(v, '__utmodule__'):
            module = v
            Test(module)
