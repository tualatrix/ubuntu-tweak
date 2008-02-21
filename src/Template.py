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
import gobject
import gettext
import gnomevfs
from gnome import ui
from UserDir import UserdirEntry
from Widgets import TweakPage

gettext.install("ubuntu-tweak", unicode = True)

(
	COLUMN_ICON,
	COLUMN_TEMPINFO,
	COLUMN_FILE
) = range(3)

class TemplateList(gtk.TreeView):
	"""The basic treeview to display the Template"""
	systemdir = "templates"
	userdir = os.path.join(os.path.expanduser("~"), "Templates")
	TARGETS = [
		('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
		('text/plain', 0, 1),
		('TEXT', 0, 2),
		('STRING', 0, 3),
		]

	def __init__(self):
		gtk.TreeView.__init__(self)

                model = gtk.ListStore(
                                gtk.gdk.Pixbuf,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING)

		self.set_model(model)

		self.__add_columns()

		self.enable_model_drag_source( gtk.gdk.BUTTON1_MASK,
						self.TARGETS,
						gtk.gdk.ACTION_DEFAULT|
						gtk.gdk.ACTION_MOVE)
		self.enable_model_drag_dest(self.TARGETS,
						gtk.gdk.ACTION_DEFAULT)

		self.connect("drag_data_get", self.on_drag_data_get_data)
		self.connect("drag_data_received", self.on_drag_data_received_data)
	def on_drag_data_get_data(self, treeview, context, selection, target_id, etime):
		print "===============get"
		treeselection = self.get_selection()
		model, iter = treeselection.get_selected()
		data = model.get_value(iter, COLUMN_FILE)
		print data
		selection.set(selection.target, 8, data)
		print "===============get============="

	def on_drag_data_received_data(self, treeview, context, x, y, selection, info, etime):
		print "==================receive "
		model = treeview.get_model()
		data = gnomevfs.format_uri_for_display(selection.data.strip())

		print data
		drop_info = treeview.get_dest_row_at_pos(x, y)
		print drop_info

		icontheme = gtk.icon_theme_get_default()
		icon = ui.icon_lookup(icontheme, 
				None,
				data)

		print icon
		pixbuf = icontheme.load_icon(icon[0], 32, 0)
		descr = os.path.splitext(os.path.basename(data))[0]

		if drop_info:
			path, position = drop_info
			iter = model.get_iter(path)

			if (position == gtk.TREE_VIEW_DROP_BEFORE or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
				model.insert_before(iter, [pixbuf, descr, data])
			else:
				model.insert_after(iter, [pixbuf, descr, data])
		else:
			model.append([pixbuf, descr, data])
		if context.action == gtk.gdk.ACTION_MOVE:
			context.finish(True, True, etime)
		return
		print "==================receive========== "

	def __add_columns(self):
		column = gtk.TreeViewColumn(self.type)

		renderer = gtk.CellRendererPixbuf()
		column.pack_start(renderer, True)
		column.set_attributes(renderer, pixbuf = COLUMN_ICON)

		renderer = gtk.CellRendererText()
		column.pack_start(renderer, True)
		column.set_attributes(renderer, text = COLUMN_TEMPINFO)

		self.append_column(column)


class EnableTemplate(TemplateList):
	"""The treeview to display the enable templates"""
	type = "Enable Template"

	def __init__(self):
		TemplateList.__init__(self)
		self.__create_model()

	def __create_model(self):
		model = self.get_model()

		icontheme = gtk.icon_theme_get_default()

		for file in os.listdir(self.userdir):
			filename = os.path.join(self.userdir, file)
			icon = ui.icon_lookup(icontheme, 
					None,
					filename)

			pixbuf = icontheme.load_icon(icon[0], 32, 0)

			iter = model.append()
			model.set(iter,
				COLUMN_ICON, pixbuf,
				COLUMN_TEMPINFO, os.path.splitext(file)[0],
				COLUMN_FILE, filename)

class SystemTemplate(TemplateList):
	"""The treeview to display the system template"""
	type = "System Template"

	def __init__(self):
		TemplateList.__init__(self)
		self.__create_model()

	def __create_model(self):
		model = self.get_model()

		icontheme = gtk.icon_theme_get_default()

		for file in filter(lambda i: i not in os.listdir(self.userdir), os.listdir(self.systemdir)):
			filename = os.path.join(os.path.abspath(self.systemdir), file)
			icon = ui.icon_lookup(icontheme, 
					None,
					filename)

			pixbuf = icontheme.load_icon(icon[0], 32, 0)

			iter = model.append()
			model.set(iter,
				COLUMN_ICON, pixbuf,
				COLUMN_TEMPINFO, os.path.splitext(file)[0],
				COLUMN_FILE, filename)

class Template(TweakPage):
        """Freedom added your docmuent template"""
        def __init__(self):
                TweakPage.__init__(self)

		self.set_title(_("Create your templates"))
		self.set_description(_("You can freely create your document template.\nIt will be added to your righ-click menu: Create Document."))

		hbox = gtk.HBox(False, 10)
		self.pack_start(hbox, True, True, 10)

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		hbox.pack_start(sw)

		tl = EnableTemplate()
		sw.add(tl)

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		hbox.pack_start(sw)

		tl = SystemTemplate()
		sw.add(tl)

		hbox = gtk.HBox(False, 10)
		self.pack_start(hbox, False, False, 5)

		button = gtk.Button("Add more templates")
		hbox.pack_end(button, False, False, 5)

if __name__ == "__main__":
	win = gtk.Window()
	win.connect('destroy', lambda *w: gtk.main_quit())
        win.set_title("Document Template")
        win.set_default_size(650, 400)
        win.set_border_width(8)

        win.add(Template())

        win.show_all()
	gtk.main()	
