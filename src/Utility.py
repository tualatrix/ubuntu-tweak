#!/usr/bin/env python

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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import pygtk
pygtk.require("2.0")
import gtk

def gtk_process_events ():
    while gtk.events_pending ():
        gtk.main_iteration ()

class Test:
	def __init__(self, model):
		win = gtk.Window()

		win.connect('destroy', lambda *w: gtk.main_quit())
		win.set_position(gtk.WIN_POS_CENTER)

		if getattr(model, "__name__", None):
			win.set_title(model.__name__)
		else:
			win.set_title(str(model))

		win.add(model())
		win.show_all()

		gtk.main()


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

