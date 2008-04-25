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
import gobject

from Constants import *
from Widgets import TweakPage, Popup, KeyGrabber, KeyModifier
from Factory import Factory

gettext.install(App, unicode = True)

(
		COLUMN_ID,
		COLUMN_TITLE,
		COLUMN_ICON,
		COLUMN_COMMAND,
		COLUMN_KEY,
		COLUMN_EDITABLE,
) = range(6)

class Keybinding(TweakPage):
	"""Setting the command of keybinding"""

	def __init__(self, parent = None):
		TweakPage.__init__(self)
		gtk.VBox.__init__(self)

		self.main_window = parent
		self.set_title(_("Set your keybinding of commands"))
		self.set_description(_("With the keybinding of commands, you can run applications more quickly.\nInput the command and grap your key, it's easy to set a keybinding.\nUse <b>Delete</b> or <b>BackSpace</b> to clean the key."))

		treeview = self.create_treeview()

		self.pack_start(treeview)
	
	def create_treeview(self):
		treeview = gtk.TreeView()

		self.model = self.__create_model()

		treeview.set_model(self.model)

		self.__add_columns(treeview)

		return treeview

	def __create_model(self):
		model = gtk.ListStore(
				gobject.TYPE_INT,
				gobject.TYPE_STRING,
				gtk.gdk.Pixbuf,
				gobject.TYPE_STRING,
				gobject.TYPE_STRING,
				gobject.TYPE_BOOLEAN,
				)

		client = gconf.client_get_default()

		for id in range(12):
			iter = model.append()
			icontheme = gtk.icon_theme_get_default()
			id = id + 1

			title = _("Command %d") % id
			command = client.get_string("/apps/metacity/keybinding_commands/command_%d" % id)
			key = client.get_string("/apps/metacity/global_keybindings/run_command_%d" % id)

			if not command: command = _("None")
			icon = icontheme.lookup_icon(command, 32, gtk.ICON_LOOKUP_NO_SVG)
			if icon: icon = icon.load_icon()

			model.set(iter,
					COLUMN_ID, id,
					COLUMN_TITLE, title,
					COLUMN_ICON, icon,
					COLUMN_COMMAND, command,
					COLUMN_KEY, key,
					COLUMN_EDITABLE, True)

		return model

	def __add_columns(self, treeview):
		model = treeview.get_model()

		column = gtk.TreeViewColumn(_("Title"), gtk.CellRendererText(), text = COLUMN_TITLE)
		treeview.append_column(column)

		column = gtk.TreeViewColumn(_("Command"))

		renderer = gtk.CellRendererPixbuf()
		column.pack_start(renderer, False)
		column.set_attributes(renderer, pixbuf = COLUMN_ICON)

		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("type", "command")
		column.pack_start(renderer, True)
		#column.set_attributes(renderer, text = COLUMN_COMMAND)
		column.set_attributes(renderer, text = COLUMN_COMMAND, editable = COLUMN_EDITABLE)
#		column = gtk.TreeViewColumn(_("Command"), renderer, text = COLUMN_COMMAND, editable = COLUMN_EDITABLE)
		treeview.append_column(column)
	
		renderer = gtk.CellRendererText()
		renderer.connect("editing-started", self.on_editing_started)
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("type", "key")
		column = gtk.TreeViewColumn(_("Key"), renderer, text = COLUMN_KEY, editable = COLUMN_EDITABLE)
		treeview.append_column(column)

	def GotKey(self, widget, key, mods, cell):
		new = gtk.accelerator_name (key, mods)
		for mod in KeyModifier:
			if "%s_L" % mod in new:
				new = new.replace ("%s_L" % mod, "<%s>" % mod)
			if "%s_R" % mod in new:
				new = new.replace ("%s_R" % mod, "<%s>" % mod)

		widget.destroy()

		client = gconf.client_get_default()
		column = cell.get_data("id")
		iter = self.model.get_iter_from_string(cell.get_data("path_string"))

		id = self.model.get_value(iter, COLUMN_ID)

		if new == "Delete" or new == "BackSpace":
			client.set_string("/apps/metacity/global_keybindings/run_command_%d" % id, "disabled")
			self.model.set_value(iter, COLUMN_KEY, _("disabled"))
		else:
			client.set_string("/apps/metacity/global_keybindings/run_command_%d" % id, new)
			self.model.set_value(iter, COLUMN_KEY, new)

	def on_editing_started(self, cell, editable, path):
		grabber = KeyGrabber(self.main_window, label = _("Grab key combination"))
		cell.set_data("path_string", path)
		grabber.hide()
		grabber.set_no_show_all(True)
		grabber.connect('changed', self.GotKey, cell)
		grabber.begin_key_grab(None)

	def on_cell_edited(self, cell, path_string, new_text, model):
		iter = model.get_iter_from_string(path_string)

		client = gconf.client_get_default()
		column = cell.get_data("id")

		type = cell.get_data("type")
		id = model.get_value(iter, COLUMN_ID)

		if type == "command":
			old = model.get_value(iter, COLUMN_COMMAND)
			if old != new_text:
				client.set_string("/apps/metacity/keybinding_commands/command_%d" % id, new_text)
				if new_text:
					icontheme = gtk.icon_theme_get_default()
					icon = icontheme.lookup_icon(new_text, 32, gtk.ICON_LOOKUP_NO_SVG)
					if icon: icon = icon.load_icon()

					model.set_value(iter, COLUMN_ICON, icon)
					model.set_value(iter, COLUMN_COMMAND, new_text)
				else:
					model.set_value(iter, COLUMN_ICON, None)
					model.set_value(iter, COLUMN_COMMAND, _("None"))
		else:
			old = model.get_value(iter, COLUMN_KEY)

			if old != new_text:
				if new_text:
					client.set_string("/apps/metacity/global_keybindings/run_command_%d" % id, new_text)
					model.set_value(iter, COLUMN_KEY, new_text)
				else:
					client.set_string("/apps/metacity/global_keybindings/run_command_%d" % id, "disabled")
					model.set_value(iter, COLUMN_KEY, _("disabled"))

if __name__ == "__main__":
	from Utility import Test
	Test(Keybinding)
