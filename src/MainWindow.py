#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
pygtk.require('2.0')
import gtk
import sys
import os
import gobject
import gettext

from Constants import *
from gnome import url_show
from SystemInfo import GnomeVersion

GNOME = int(GnomeVersion.minor)

from Computer import Computer
from Session import Session
from AutoStart import AutoStart
from Icon import Icon
if GNOME >= 20:
	from Compiz import Compiz
	from UserDir import UserDir
	from Templates import Templates
else:
	Compiz = None
	UserDir = None
	Templates = None
from Scripts import Scripts
from Keybinding import Keybinding
from PowerManager import PowerManager
from Gnome import Gnome
from Nautilus import Nautilus
from LockDown import LockDown
from Metacity import Metacity

(
        NUM_COLUMN,
        ICON_COLUMN,
        NAME_COLUMN,
	PAGE_COLUMN,
	Version_COLUMN,
        TOTAL_COLUMN,
) = range(6)

(
        WELCOME_PAGE,
	COMPUTER_PAGE,
	STARTUP_PAGE,
		SESSION_PAGE,
		AUTOSTART_PAGE,
	DESKTOP_PAGE,
		ICON_PAGE,
		METACITY_PAGE,
		COMPIZ_PAGE,
	PERSONAL_PAGE,
		USERDIR_PAGE,
		TEMPLATES_PAGE,
		SCRIPTS_PAGE,
		KEYBINDING_PAGE,
	SYSTEM_PAGE,
		GNOME_PAGE,
		NAUTILUS_PAGE,
		POWER_PAGE,
	SECURITY_PAGE,
		SECU_OPTIONS_PAGE,
	TOTAL_PAGE
) = range(21)

icons = \
[
	"pixmaps/welcome.png",
	"pixmaps/computer.png",
	"pixmaps/startup.png",
	"pixmaps/session.png",
	"pixmaps/autostart.png",
	"pixmaps/desktop.png",
	"pixmaps/icon.png",
	"pixmaps/metacity.png",
	"pixmaps/compiz-fusion.png",
	"pixmaps/personal.png",
	"pixmaps/userdir.png",
	"pixmaps/template.png",
	"pixmaps/scripts.png",
	"pixmaps/keybinding.png",
	"pixmaps/system.png",
	"pixmaps/gnome.png",
	"pixmaps/nautilus.png",
	"pixmaps/powermanager.png",
	"pixmaps/security.png",
	"pixmaps/lockdown.png",
]

def Welcome():
	vbox = gtk.VBox(False, 0)

	label = gtk.Label()
	label.set_markup(_("<span size=\"xx-large\">Welcome to <b>Ubuntu Tweak!</b></span>\n\n\nThis is a tool for Ubuntu which makes it easy to change hidden \nsystem and desktop settings.\n\nAnd it is usable on other distributions.\n\nYou can redistribute it under GPL license.\n\nIf you have any suggestions, Please visit the website in \"About\" and \nshare ideas with me. \n\nEnjoy!"))
	label.set_justify(gtk.JUSTIFY_FILL)
	vbox.pack_start(label, False, False, 50)

	hbox = gtk.HBox(False, 0)
	vbox.pack_start(hbox, False, False, 0)
		
	return vbox

def Blank():
	vbox = gtk.VBox(True, 0)

	label = gtk.Label()
	label.set_markup(_("<span size=\"xx-large\">Please select the child item</span>"))
	vbox.pack_start(label, False, False, 0)

	return vbox

startup = \
[
	[SESSION_PAGE, icons[SESSION_PAGE], _("Session Control"), Session, 0],
	[AUTOSTART_PAGE, icons[AUTOSTART_PAGE], _("Auto Start"), AutoStart, 0],
]

desktop = \
[
	[ICON_PAGE, icons[ICON_PAGE], _("Desktop Icon"), Icon, 0],
	[METACITY_PAGE, icons[METACITY_PAGE], _("Metacity"), Metacity, 0],
	[COMPIZ_PAGE, icons[COMPIZ_PAGE], _("Compiz Fusion"), Compiz, 20],
]

personal = \
[
	[USERDIR_PAGE, icons[USERDIR_PAGE], _("User Folder"), UserDir, 20],
	[TEMPLATES_PAGE, icons[TEMPLATES_PAGE], _("Templates"), Templates, 20],
	[SCRIPTS_PAGE, icons[SCRIPTS_PAGE], _("Scripts"), Scripts, 0],
	[KEYBINDING_PAGE, icons[KEYBINDING_PAGE], _("Keybinding"), Keybinding, 0],
]

system = \
[
	[GNOME_PAGE, icons[GNOME_PAGE], _("GNOME"), Gnome, 0],
	[NAUTILUS_PAGE, icons[NAUTILUS_PAGE], _("Nautilus"), Nautilus, 0],
	[POWER_PAGE, icons[POWER_PAGE], _("Power Manager"), PowerManager, 0],
]

security = \
[
	[SECU_OPTIONS_PAGE, icons[SECU_OPTIONS_PAGE], _("Security Options"), LockDown, 0]
]

itemlist = \
[
	[WELCOME_PAGE, icons[WELCOME_PAGE], _("Welcome"), Welcome, None],
	[COMPUTER_PAGE, icons[COMPUTER_PAGE], _("Computer"), Computer, None],
	[STARTUP_PAGE, icons[STARTUP_PAGE], _("Startup"), Blank, startup],
	[DESKTOP_PAGE, icons[DESKTOP_PAGE], _("Desktop"), Blank, desktop],
	[PERSONAL_PAGE, icons[PERSONAL_PAGE], _("Personal"), Blank, personal],
	[SYSTEM_PAGE, icons[SYSTEM_PAGE], _("System"), Blank, system],
	[SECURITY_PAGE, icons[SECURITY_PAGE], _("Security"), Blank, security],
]

class MainWindow(gtk.Window):
	"""the main Window of Ubuntu Tweak"""

	def __init__(self):
		gtk.Window.__init__(self)
		self.connect("destroy", self.destroy)
		self.set_title("Ubuntu Tweak")
		self.set_default_size(650, 680)
		self.set_position(gtk.WIN_POS_CENTER)
		self.set_border_width(10)
		self.set_icon_from_file("pixmaps/ubuntu-tweak.png")

		vbox = gtk.VBox(False, 0)
		self.add(vbox)

		eventbox = gtk.EventBox()
		hbox = gtk.HBox(False, 0)
		eventbox.add(hbox)
		eventbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(8448, 8448, 8448))
		vbox.pack_start(eventbox, False, False, 0)

		banner_left = gtk.Image()
		banner_left.set_from_file("pixmaps/banner_left.png")
		hbox.pack_start(banner_left, False, False, 0)
		banner_right = gtk.Image()
		banner_right.set_from_file("pixmaps/banner_right.png")
		hbox.pack_end(banner_right, False, False, 0)

		hpaned = gtk.HPaned()
		vbox.pack_start(hpaned, True, True, 0)

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_size_request(150, -1)
		hpaned.pack1(sw)

		model = self.__create_model()
		self.treeview = gtk.TreeView(model)
		self.__add_columns(self.treeview)
		selection = self.treeview.get_selection()
		selection.connect("changed", self.selection_cb)

		sw.add(self.treeview)

		self.notebook = self.create_notebook()
		hpaned.pack2(self.notebook)

		hbox = gtk.HBox(False,5)
		vbox.pack_start(hbox, False, False, 5)
		button = gtk.Button(stock = gtk.STOCK_ABOUT)
		button.connect("clicked", self.show_about)
		hbox.pack_start(button, False, False, 0)
		button = gtk.Button(stock = gtk.STOCK_QUIT)
		button.connect("clicked", self.destroy);
		hbox.pack_end(button, False, False, 0)
		
		self.show_all()

	def __create_model(self):
		model = gtk.TreeStore(
				gobject.TYPE_INT,
				gtk.gdk.Pixbuf,
				gobject.TYPE_STRING)
		i = 0

		for item in itemlist:
			icon = gtk.gdk.pixbuf_new_from_file(item[ICON_COLUMN])
			iter = model.append(None)
			model.set(iter,
				NUM_COLUMN, i,
				ICON_COLUMN, icon,
				NAME_COLUMN, item[NAME_COLUMN]
			)
			if item[-1]:
				for child_item in item[-1]:
					if  GNOME >= child_item[Version_COLUMN]:
						i = i + 1
						icon = gtk.gdk.pixbuf_new_from_file(child_item[ICON_COLUMN])
						child_iter = model.append(iter)
						model.set(child_iter,
							NUM_COLUMN, i,
							ICON_COLUMN, icon,
							NAME_COLUMN, child_item[NAME_COLUMN]
						)
					else:
						continue

			i = i + 1

		return model

	def selection_cb(self, widget, data = None):
		if not widget.get_selected():
			return
		model, iter = widget.get_selected()

		if iter:
			path = model.get_path(iter)
			self.treeview.expand_row(path, True)

			if model.iter_has_child(iter):
				child_iter = model.iter_children(iter)
				self.notebook.set_current_page(model.get_value(child_iter, NUM_COLUMN))
				widget.select_iter(child_iter)
			else:
				self.notebook.set_current_page(model.get_value(iter, NUM_COLUMN))

	def __add_columns(self, treeview):
		renderer = gtk.CellRendererText()

		column = gtk.TreeViewColumn("Num",renderer,text = NUM_COLUMN)
		column.set_visible(False)
		treeview.append_column(column)

		column = gtk.TreeViewColumn("Title")
		column.set_spacing(5)

		renderer = gtk.CellRendererPixbuf()
		column.pack_start(renderer, False)
		column.set_attributes(renderer, pixbuf = ICON_COLUMN)

		renderer = gtk.CellRendererText()
		column.pack_start(renderer, True)
		column.set_attributes(renderer, text = NAME_COLUMN)

		treeview.set_headers_visible(False)
		treeview.append_column(column)

	def create_notebook(self):
		notebook = gtk.Notebook()
		notebook.set_scrollable(True)
		notebook.set_show_tabs(False)

		for item in itemlist:
			page = item[PAGE_COLUMN]
			notebook.append_page(page(), None)

			if item[-1]:
				for child_item in item[-1]:
					if GNOME >= child_item[Version_COLUMN]:
						page = child_item[PAGE_COLUMN]
						notebook.append_page(page(self), None)
					else:
						continue

		return notebook

	def click_website(self, dialog, link, data = None):
		url_show(link)
	
	def show_about(self, data = None):
		gtk.about_dialog_set_url_hook(self.click_website)
		gtk.about_dialog_set_email_hook(self.click_website)

		about = gtk.AboutDialog()
		about.set_transient_for(self)
		about.set_icon_from_file("pixmaps/ubuntu-tweak.png")
		about.set_name("Ubuntu Tweak")
		about.set_version(Version)
		about.set_website("http://ubuntu-tweak.com")
		about.set_website_label("ubuntu-tweak.com")
		about.set_logo(self.get_icon())
		about.set_comments(_("Ubuntu Tweak is a tool for Ubuntu that makes it easy to configure your system and desktop settings."))
		about.set_authors(["TualatriX <tualatrix@gmail.com>"])
		about.set_copyright("Copyright © 2008 TualatriX")
		about.set_wrap_license(True)
		about.set_license("Ubuntu Tweak is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.\n\
Ubuntu Tweak is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.\n\
You should have received a copy of the GNU General Public License along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA")
		about.set_translator_credits(_("translator-credits"))
		about.set_artists(["Medical-Wei <a790407@hotmail.com>", "m.Sharp <mac.sharp@gmail.com>", "taiwan ock ting <a2d8a4v@gmail.com>"])
		about.run()
		about.destroy()

	def destroy(self, widget, data = None):
		gtk.main_quit()

	def main(self):
		gtk.main()
