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
import gettext
import gconf

from Constants import *
from Widgets import Mediator
from Factory import Factory

gettext.install(App, unicode = True)

computer_icon = \
{
	"label" : _("Show \"Computer\" icon on desktop"),
	"rename" : _("Rename the \"Computer\" icon: "),
	"visible" : "computer_icon_visible",
	"name" : "computer_icon_name",
	"icon" : "gnome-fs-client"
}

home_icon = \
{
	"label" : _("Show \"Home\" icon on desktop"),
	"rename" : _("Rename the \"Home\" icon: "),
	"visible" : "home_icon_visible",
	"name" : "home_icon_name",
	"icon" : "gnome-fs-home"
}
	
trash_icon = \
{
	"label" : _("Show \"Trash\" icon on desktop"),
	"rename" : _("Rename the \"Trash\" icon: "),
	"visible" : "trash_icon_visible",
	"name" : "trash_icon_name",
	"icon" : "gnome-fs-trash-empty"
}

desktop_icon = (computer_icon, home_icon, trash_icon)

class DesktopIcon(gtk.VBox, Mediator):
	def __init__(self, item):
		gtk.VBox.__init__(self)

		self.show_button = Factory.create("cgconfcheckbutton", item["label"], item["visible"], self)
		self.pack_start(self.show_button, False, False, 0)

		self.show_hbox = gtk.HBox(False, 10)
		self.pack_start(self.show_hbox, False, False, 0)

		if not self.show_button.get_active():
			self.show_hbox.set_sensitive(False)

		icon = gtk.image_new_from_icon_name(item["icon"], gtk.ICON_SIZE_DIALOG)
		self.show_hbox.pack_start(icon, False, False, 0)

		self.rename_button = Factory.create("strgconfcheckbutton", item["rename"], item["name"], self)
		vbox = gtk.VBox(False, 5)
		self.show_hbox.pack_start(vbox, False, False, 0)
		vbox.pack_start(self.rename_button, False, False, 0)

		self.entry = Factory.create("gconfentry", item["name"])
		if not self.rename_button.get_active():
			self.entry.set_sensitive(False)
		vbox.pack_start(self.entry, False, False, 0)

	def colleague_changed(self):
		self.show_hbox.set_sensitive(self.show_button.get_active())
		self.entry.set_sensitive(self.rename_button.get_active())

class Icon(gtk.VBox, Mediator):
	"""Desktop Icon settings"""

	def __init__(self, parent = None):
		gtk.VBox.__init__(self, False, 5)

		self.set_border_width(5)

		label = gtk.Label()
		label.set_markup(_("<b>Desktop Icon settings</b>"))
		label.set_alignment(0, 0)
		self.pack_start(label, False, False, 0)

		self.show_button = Factory.create("cgconfcheckbutton", _("Show desktop icons"), "show_desktop", self)
		self.pack_start(self.show_button, False, False, 0)

		self.show_button_box = gtk.HBox(False, 10)
		self.pack_start(self.show_button_box, False, False,0)

		if not self.show_button.get_active():
			self.show_button_box.set_sensitive(False)

		label = gtk.Label(" ")
		self.show_button_box.pack_start(label, False, False, 0)

		vbox = gtk.VBox(False, 5)
		self.show_button_box.pack_start(vbox, False, False, 0)

		client = gconf.client_get_default()
		for item in desktop_icon:
			vbox.pack_start(DesktopIcon(item), False, False, 0)

		button = Factory.create("gconfcheckbutton", _("Show \"Network\" icon on desktop"), "network_icon_visible")
		vbox.pack_start(button, False, False, 0)

		button = Factory.create("gconfcheckbutton", _("Show Mounted Volumes on desktop"), "volumes_visible")
		vbox.pack_start(button, False, False, 0)

		button = Factory.create("gconfcheckbutton", _("Use Home Folder as the desktop(Need Logout)"), "desktop_is_home_dir")
		vbox.pack_start(button, False, False, 0)

	def colleague_changed(self):
		self.show_button_box.set_sensitive(self.show_button.get_active())

if __name__ == "__main__":
	from Utility import Test
	Test(Icon)
