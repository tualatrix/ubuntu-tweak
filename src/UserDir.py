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
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext
from Constants import *
from IniFile import IniFile
from Widgets import TweakPage, EntryBox, show_info

gettext.install(App, unicode = True)

class UserdirFile(IniFile):
	"""Class to parse userdir file"""
	filename = os.path.join(os.path.expanduser("~"), ".config/user-dirs.dirs")
	def __init__(self):
		IniFile.__init__(self, self.filename)

class UserDir(TweakPage):
        """Setting the user default dictories"""
	diritems = {	"XDG_DESKTOP_DIR": _("Desktop Folder"),
			"XDG_DOWNLOAD_DIR": _("Download Folder"),
			"XDG_TEMPLATES_DIR": _("Templates Folder"),
			"XDG_PUBLICSHARE_DIR": _("Public Folder"),
			"XDG_DOCUMENTS_DIR": _("Document Folder"),
			"XDG_MUSIC_DIR": _("Music Folder"),
			"XDG_PICTURES_DIR": _("Pictures Folder"),
			"XDG_VIDEOS_DIR": _("Videos Folder")}
        def __init__(self, parent = None):
		TweakPage.__init__(self)

		self.set_title(_("Set your document folders"))
		self.set_description(_("You can change the default document folders.\nDon't change the Desktop folder in normal case."))

		table = self.create_table()
		self.pack_start(table, False, False, 5)

		hbox = gtk.HBox(False, 0)
		self.pack_start(hbox, False, False, 5)

		button = gtk.Button(stock = gtk.STOCK_APPLY)
		button.connect("clicked", self.on_apply_clicked)
		hbox.pack_end(button, False, False, 0)

	def on_apply_clicked(self, widget, data = None):
		os.system('xdg-user-dirs-gtk-update')
		show_info(_("Update successfully!"), type = gtk.MESSAGE_INFO)

	def create_table(self):
		table = gtk.Table(8, 3)

		ue = UserdirFile()
		length = len(ue.content.keys())

		for item, value in self.diritems.items():
			label = gtk.Label()
			label.set_markup("<b>%s</b>" % value)

			entry = gtk.Entry()

			prefix = ue.get(item).strip('"').split("/")[0]
			if prefix:
				dirpath = os.getenv("HOME") + "/"  + "/".join([dir for dir in ue.get(item).strip('"').split("/")[1:]])
			else:
				dirpath = ue.get(item).strip('"')

			entry.set_text(dirpath)
			entry.set_editable(False)

			button = gtk.Button(_("_Browse"))
			button.connect("clicked", self.on_browser_clicked, (item, entry))

			offset = self.diritems.keys().index(item)

			table.attach(label, 0, 1, offset, offset + 1, xoptions = gtk.FILL, xpadding = 5, ypadding = 5)
			table.attach(entry, 1, 2, offset, offset + 1, xpadding = 5, ypadding = 5)
			table.attach(button, 2, 3, offset, offset + 1, xoptions = gtk.FILL, xpadding = 5, ypadding = 5)

		return table

	def on_browser_clicked(self, widget, data = None):
		item, entry = data
		dialog = gtk.FileChooserDialog(_("Select a new folder"),
				action = gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
				buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
		dialog.set_current_folder(os.getenv("HOME"))
		if dialog.run() == gtk.RESPONSE_ACCEPT:
			ue = UserdirFile()
			realpath = dialog.get_filename()
			dirname = '/'.join([path for path in realpath.split('/')[:3]])
			if dirname == os.getenv("HOME"):
				folder = '"$HOME/' + "/".join([dir for dir in realpath.split('/')[3:]]) + '"'
			else:
				folder = '"' + realpath + '"'
			ue.set(item, folder)
			ue.write()
			if dirname == os.getenv("HOME"):
				folder = os.getenv("HOME") + "/" +  "/".join([dir for dir in realpath.split('/')[3:]])
			else:
				folder = folder.strip('"')
			entry.set_text(folder)
		dialog.destroy()

if __name__ == "__main__":
	win = gtk.Window()
	win.connect('destroy', lambda *w: gtk.main_quit())
        win.set_title("User Dir")
        win.set_default_size(650, 400)
        win.set_border_width(8)

        win.add(UserDir())

        win.show_all()
	gtk.main()
