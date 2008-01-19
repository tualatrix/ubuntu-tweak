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

from Widgets import GConfCheckButton, ItemBox

gettext.install("ubuntu-tweak", unicode = True)

class Session(gtk.VBox):
	"""GNOME Session control"""

	def __init__(self):
		gtk.VBox.__init__(self)

		self.pack_start(self.session_control_box(), False, False, 0)

		box = ItemBox(_("<b>Click the large button to change Splash screen</b>"), (self.splash_hbox(),))
		self.pack_start(box, False, False, 0)

	def change_splash_cb(self, widget, data = None):
		dialog = gtk.FileChooserDialog(_("Choose a Splash image"),action = gtk.FILE_CHOOSER_ACTION_OPEN, buttons = (gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
		filter = gtk.FileFilter()
		filter.set_name(_("PNG image (*.png)"))
		filter.add_mime_type("image/png")
		dialog.set_current_folder(self.filedir)
		dialog.add_filter(filter)

		if dialog.run() == gtk.RESPONSE_ACCEPT:
			client = gconf.client_get_default()
			filename = dialog.get_filename()
			data.set_text(os.path.basename(filename))
			self.filedir = os.path.dirname(filename)
			self.original_preview = gtk.gdk.pixbuf_new_from_file(filename)
			x = self.original_preview.get_width()
			y = self.original_preview.get_height()
			if x * 180 / y > 240:
				y = y * 240 / x
				x = 240
			else:
				x = x * 180 / y
				y = 180

			self.new_preview = self.original_preview.scale_simple(x , y, gtk.gdk.INTERP_NEAREST)
			self.image.set_from_pixbuf(self.new_preview)
			client.set_string("/apps/gnome-session/options/splash_image", filename)
		dialog.destroy()

	def show_splash_toggled(self, widget, data = None):
                client = gconf.client_get_default()
                if widget.get_active():
                        client.set_bool("/apps/gnome-session/options/show_splash_screen", True)
			self.button.set_sensitive(True)
                else:
                        client.set_bool("/apps/gnome-session/options/show_splash_screen", False)
			self.button.set_sensitive(False)

	def splash_hbox(self):
		client = gconf.client_get_default()
		filename = client.get_string("/apps/gnome-session/options/splash_image")
		self.filedir = os.path.dirname(filename)
		try:
			f = open(filename)
		except IOError:
			print "Failed to open file '%s': No such file or directory" % filename
		else:
			self.original_preview = gtk.gdk.pixbuf_new_from_file(filename)
			x = self.original_preview.get_width()
			y = self.original_preview.get_height()

			if x * 180 / y > 240:
				y = y * 240 / x
				x = 240
			else:
				x = x * 180 / y
				y = 180

			self.new_preview = self.original_preview.scale_simple(x, y, gtk.gdk.INTERP_NEAREST)

		hbox = gtk.HBox(False, 0)
		self.button = gtk.Button()
		hbox.pack_start(self.button, True, False, 0)
		hbox.set_size_request(256, -1)

		if client.get_bool("/apps/gnome-session/options/show_splash_screen"):
			self.button.set_sensitive(True)
		else:
			self.button.set_sensitive(False)

		vbox = gtk.VBox(False, 2)
		self.button.add(vbox)

		alignment = gtk.Alignment(0.5, 0.5, 1, 1)
		alignment.set_size_request(240, 180)
		vbox.pack_start(alignment, False, False, 0)

		self.image = gtk.Image()
		if getattr(self, "new_preview", False):
			self.image.set_from_pixbuf(self.new_preview)
		alignment.add(self.image)

		label = gtk.Label(os.path.basename(filename))
		vbox.pack_end(label, False, False, 0)

		self.button.connect("clicked", self.change_splash_cb, label)

		return hbox

	def session_control_box(self):
		button = GConfCheckButton(_("Automatically save changes to session"), "/apps/gnome-session/options/auto_save_session") 
		button2 = GConfCheckButton(_("Show Logout prompt"), "/apps/gnome-session/options/logout_prompt")
		button3 = GConfCheckButton(_("Allow TCP Connections(Remote Connect)"), "/apps/gnome-session/options/allow_tcp_connections")
		button4 = GConfCheckButton(_("Show Splash screen"), "/apps/gnome-session/options/show_splash_screen", extra = self.show_splash_toggled)

		box = ItemBox(_("<b>Session Control</b>"), (button, button2, button3, button4))
		return box
