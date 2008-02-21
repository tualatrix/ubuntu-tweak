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
import os
import gconf
import gettext
from IniFile import IniFile
from Widgets import GConfCheckButton, ItemBox, TweakPage, EntryBox

gettext.install("ubuntu-tweak", unicode = True)

class UserdirEntry(IniFile):
	"""Class to parse userdir"""
	filename = os.path.join(os.path.expanduser("~"), ".config/user-dirs.dirs")
	def __init__(self):
		IniFile.__init__(self, self.filename)

class UserdirEdit():
	def __init__(self, label, text):
		EntryBox.__init__(self, label, text)

		button = gtk.Button(stock = gtk.STOCK_DIRECTORY)
		self.pack_end(button)

class UserDir(TweakPage):
        """Setting the user default dictories"""
        def __init__(self):
		TweakPage.__init__(self)

		self.set_title(_("Change your document diectory"))
		self.set_description(_("Setting the default user directory, so that it can be more freely"))

		hbox = gtk.HBox(False, 5)
		self.pack_start(hbox, False, False, 0)

		label = gtk.Label("Desktop")
		hbox.pack_start(label, False, False, 5)
		entry = gtk.Entry()
		hbox.pack_start(entry)
		button = gtk.Button("Change")
		hbox.pack_end(button, False, False, 5)

if __name__ == "__main__":
	win = gtk.Window()
	win.connect('destroy', lambda *w: gtk.main_quit())
        win.set_title("User Dir")
        win.set_default_size(650, 400)
        win.set_border_width(8)

        win.add(UserDir())

        win.show_all()
	gtk.main()
