#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configure tool
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
import gtk
import gobject
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from ubuntutweak.common.consts import *

class Test:
    def __init__(self, model):
        gtk.gdk.threads_init()

        win = gtk.Window()
        win.connect('destroy', lambda *w: gtk.main_quit())
        win.set_position(gtk.WIN_POS_CENTER)
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

        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()

class ManyTest:
    def __init__(self, widgets):
        win = gtk.Window()

        win.connect('destroy', lambda *w: gtk.main_quit())
        win.set_position(gtk.WIN_POS_CENTER)

        win.set_title("Many test")
        
        vbox = gtk.VBox(False, 10)
        win.add(vbox)

        for widget in widgets:
            vbox.pack_start(widget, False, False, 5)

        win.show_all()

        gtk.main()

if __name__ == '__main__':
    from modules import ModuleLoader
    gobject.threads_init()
    loader = ModuleLoader(sys.argv[1])
    Test(loader.id_table.values()[0])
