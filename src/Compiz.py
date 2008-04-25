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
import os
import gobject
try:
	import compizconfig as ccs
	import ccm
	if ccm.Version == "0.7.4":
		DISABLE = False
	else:
		DISABLE = True
except ImportError:
	DISABLE = True
from Constants import *
from Widgets import ListPack

gettext.install(App, unicode = True)

plugins = \
[
	"expo",
	"scale",
	"core",
	"widget",
]

plugins_settings = \
{
	
	"expo": "expo_edge",
	"scale": "initiate_all_edge",
	"core": "show_desktop_edge",
	"widget": "toggle_edge",
}

class CompizSetting:
	if not DISABLE:
		context = ccs.Context()

class OpacityMenu(gtk.CheckButton, CompizSetting):
	menu_match = 'Tooltip | Menu | PopupMenu | DropdownMenu'
	def __init__(self, label):
		gtk.CheckButton.__init__(self, label)

		self.plugin = self.context.Plugins['core']
		self.setting_matches = self.plugin.Screens[0]['opacity_matches']
		self.setting_values = self.plugin.Screens[0]['opacity_values']

		if self.menu_match in self.setting_matches.Value:
			self.set_active(True)

		self.connect("toggled", self.on_button_toggled)

	def on_button_toggled(self, widget, data = None):
		if self.get_active():
			self.setting_matches.Value = [self.menu_match]
			self.setting_values.Value = [90]
		else:
			index = self.setting_matches.Value.index(self.menu_match)
			self.setting_matches.Value = []
			self.setting_values.Value = []
		self.context.Write()

class WobblyMenu(gtk.CheckButton, CompizSetting):
	def __init__(self, label, mediator):
		gtk.CheckButton.__init__(self, label)

		self.mediator = mediator
		self.plugin = self.context.Plugins['wobbly']
		self.setting = self.plugin.Screens[0]['map_window_match']
		
		if self.setting.Value == self.setting.DefaultValue and self.plugin.Enabled:
			self.set_active(True)

		self.connect("toggled", self.on_button_toggled)

	def on_button_toggled(self, widget, data = None):
		if self.get_active():
			conflicts = self.plugin.Enabled and self.plugin.DisableConflicts or self.plugin.EnableConflicts
			conflict = ccm.PluginConflict(self.plugin, conflicts)
			if conflict.Resolve():
				self.mediator.snap.set_active(False)
				if not self.plugin.Enabled: self.plugin.Enabled = True
				self.setting.Reset()
		else:
			self.setting.Value = ""

		self.context.Write()

		if self.setting.Value == self.setting.DefaultValue and self.plugin.Enabled:
			self.set_active(True)
		else:
			self.set_active(False)

class WobblyWindow(gtk.CheckButton, CompizSetting):
	def __init__(self, label, mediator):
		gtk.CheckButton.__init__(self, label)

		self.mediator = mediator
		self.plugin = self.context.Plugins['wobbly']
		self.setting = self.plugin.Screens[0]['move_window_match']
		
		if self.setting.Value == self.setting.DefaultValue and self.plugin.Enabled:
			self.set_active(True)

		self.connect("toggled", self.on_button_toggled)

	def on_button_toggled(self, widget, data = None):
		if self.get_active():
			conflicts = self.plugin.Enabled and self.plugin.DisableConflicts or self.plugin.EnableConflicts
			conflict = ccm.PluginConflict(self.plugin, conflicts)
			if conflict.Resolve():
				self.mediator.snap.set_active(False)
				if not self.plugin.Enabled: self.plugin.Enabled = True
				self.setting.Reset()
		else:
			self.setting.Value = ""

		self.context.Write()

		if self.setting.Value == self.setting.DefaultValue and self.plugin.Enabled:
			self.set_active(True)
		else:
			self.set_active(False)

class SnapWindow(gtk.CheckButton, CompizSetting):
	def __init__(self, label, mediator):
		gtk.CheckButton.__init__(self, label)

		self.mediator = mediator
		self.plugin = self.context.Plugins['snap']
		
		self.set_active(self.plugin.Enabled)

		self.connect("toggled", self.on_button_toggled)

	def on_button_toggled(self, widget, data = None):
		if self.get_active():
			conflicts = self.plugin.Enabled and self.plugin.DisableConflicts or self.plugin.EnableConflicts
			conflict = ccm.PluginConflict(self.plugin, conflicts)
			if conflict.Resolve():
				self.plugin.Enabled = True
				self.mediator.wobbly_w.set_active(False)
				self.mediator.wobbly_m.set_active(False)
		else:
			self.plugin.Enabled = False

		self.context.Write()

		self.set_active(self.plugin.Enabled)

class Compiz(gtk.VBox, CompizSetting):
	"""Compiz Fusion tweak"""

	def __init__(self, parent = None):
		gtk.VBox.__init__(self)

		vbox = gtk.VBox(False, 0)
		vbox.set_border_width(5)

		label = gtk.Label()
		label.set_markup(_("<b>Edge Setting</b>"))
		label.set_alignment(0, 0)
		vbox.pack_start(label, False, False, 0)
		self.pack_start(vbox, False, False, 0)

		hbox = gtk.HBox(False, 0)
		self.pack_start(hbox, False, False, 0)
		hbox.pack_start(self.create_edge_setting(), True, False, 0)

		self.snap = SnapWindow(_("Snapping Windows"), self)
		self.wobbly_w = WobblyWindow(_("Wobbly Windows"), self);

		box = ListPack(_("<b>Window Effects</b>"), (self.snap, self.wobbly_w))
		self.pack_start(box, False, False, 0)

		button1 = OpacityMenu(_("Opacity Menu"))
		self.wobbly_m = WobblyMenu(_("Wobbly Menu"), self)

		box = ListPack(_("<b>Menu Effects</b>"), (button1, self.wobbly_m))
		self.pack_start(box, False, False, 0)

	def combo_box_changed_cb(self, widget, edge):
		"""If the previous setting is none, then select the add edge"""
		if widget.previous:
			self.change_edge(widget, edge)
		else:
			self.add_edge(widget, edge)
			
	def change_edge(self, widget, edge):
		previous = widget.previous

		plugin = self.context.Plugins[previous]
		setting = plugin.Display[plugins_settings[previous]]
		setting.Value = ""
		self.context.Write()

		self.add_edge(widget, edge)	

	def add_edge(self, widget, edge):
		i = widget.get_active()
		if i == 4:
			widget.previous = None
		else:
			plugin = self.context.Plugins[plugins[i]]
			setting = plugin.Display[plugins_settings[plugins[i]]]
			setting.Value = edge
			self.context.Write()
			widget.previous = plugins[i]

	def create_edge_combo_box(self, edge):
		combobox = gtk.combo_box_new_text()
		combobox.append_text(_("Expo"))
		combobox.append_text(_("Pick Windows"))
		combobox.append_text(_("Show Desktop"))
		combobox.append_text(_("Widget"))
		combobox.append_text("-")
		combobox.set_active(4)
		combobox.previous = None

		for k, v in plugins_settings.items():
			plugin = self.context.Plugins[k]
			if not plugin.Enabled:
				plugin.Enabled = True
				self.context.Write()
			setting = plugin.Display[v]
			if setting.Value == edge:
				combobox.previous = k
				combobox.set_active(plugins.index(k))

		combobox.connect("changed", self.combo_box_changed_cb, edge)

		return combobox

	def create_edge_setting(self):
		hbox = gtk.HBox(False, 0)

		vbox = gtk.VBox(False, 0)
		hbox.pack_start(vbox, False, False, 0)

		combobox = self.create_edge_combo_box("TopLeft")
		vbox.pack_start(combobox, False, False, 0)

		combobox = self.create_edge_combo_box("BottomLeft")
		vbox.pack_end(combobox, False, False, 0)

		client = gconf.client_get_default()
		wallpaper = client.get_string("/desktop/gnome/background/picture_filename")

		if wallpaper:
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(wallpaper, 160, 100)
		else:
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size("/usr/share/backgrounds/warty-final-ubuntu.png", 160, 100)
		image = gtk.image_new_from_pixbuf(pixbuf)
		hbox.pack_start(image, False, False, 0)
		
		vbox = gtk.VBox(False, 0)
		hbox.pack_start(vbox, False, False, 0)
		
		combobox = self.create_edge_combo_box("TopRight")
		vbox.pack_start(combobox, False, False, 0)

		combobox = self.create_edge_combo_box("BottomRight")
		vbox.pack_end(combobox, False, False, 0)

		return hbox

if __name__ == "__main__":
	from Utility import Test
	Test(Compiz)
