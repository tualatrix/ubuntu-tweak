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
import shutil
import gobject
import gettext
import gnomevfs
from Constants import *
from gnome import ui
from UserDir import UserdirFile
from Widgets import TweakPage, MessageDialog

gettext.install(App, unicode = True)

(
	COLUMN_ICON,
	COLUMN_TEMPINFO,
	COLUMN_FILE,
) = range(3)

class AbstractTempates:
	systemdir = os.path.join(os.path.expanduser("~"), ".ubuntu-tweak/templates")
	userdir = os.getenv("HOME") + "/"  + "/".join([dir for dir in UserdirFile().get('XDG_TEMPLATES_DIR').strip('"').split("/")[1:]])

class DefaultTemplates(AbstractTempates):
	"""This class use to create the default templates"""
	templates = {
			"HTML document.html": _("HTML document"),
			"ODB Database.odb": _("ODB Database"),
			"ODS Spreadsheet.ods": _("ODS Spreadsheet"),
			"ODT Document.dot": _("ODT Document"),
			"Plain text document.txt": _("Plain text document"),
			"ODP Presentation.odp": _("ODP Presentation"),
			"Python script.py": _("Python script"),
			"Shell script.sh": _("Shell script")
			}

	def create(self):
		if not os.path.exists(self.systemdir):
			os.makedirs(self.systemdir)
		for file, des in self.templates.items():
			realname = "%s.%s" % (des, file.split('.')[1])
			if not os.path.exists(self.systemdir + realname):
				shutil.copy("templates/%s" % file, self.systemdir + "/" + realname)

	def remove(self):
		if not os.path.exists(self.systemdir):
			return 
		if os.path.isdir(self.systemdir): 
			for root, dirs, files in os.walk(self.systemdir, topdown=False):
				for name in files:
					os.remove(os.path.join(root, name))
				for name in dirs:
					os.rmdir(os.path.join(root, name))
					os.rmdir(self.systemdir)
		else:
			os.unlink(self.systemdir)
		return

class TemplateList(gtk.TreeView, AbstractTempates):
	"""The basic treeview to display the Template"""
	type = ''

	TARGETS = [
		('text/plain', 0, 1),
		('TEXT', 0, 2),
		('STRING', 0, 3),
		]

	def __init__(self):
		gtk.TreeView.__init__(self)

		self.set_rules_hint(True)

                model = gtk.ListStore(
                                gtk.gdk.Pixbuf,
                                gobject.TYPE_STRING,
                                gobject.TYPE_STRING)

		self.set_model(model)

		self.__add_columns()

		menu = self.create_popup_menu()
		menu.show_all()
		self.connect("button_press_event", self.button_press_event, menu)

		self.enable_model_drag_source( gtk.gdk.BUTTON1_MASK,
						self.TARGETS,
						gtk.gdk.ACTION_DEFAULT|
						gtk.gdk.ACTION_MOVE)
		self.enable_model_drag_dest(self.TARGETS,
						gtk.gdk.ACTION_DEFAULT)

		self.connect("drag_data_get", self.on_drag_data_get_data)
		self.connect("drag_data_received", self.on_drag_data_received_data)

	def create_popup_menu(self):
		menu = gtk.Menu()

		delete = gtk.MenuItem(_("Delete this template"))
		delete.connect("activate", self.on_delete_template)
		
		menu.append(delete)
		menu.attach_to_widget(self, None)

		return menu

	def on_delete_template(self, widget, data = None):
		model, iter = self.get_selection().get_selected()
		if iter:
			filepath = model.get_value(iter, COLUMN_FILE)
			os.remove(filepath)
			model.remove(iter)

	def button_press_event(self, widget, event, data = None):
		if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
			data.popup(None, None, None, event.button, event.time)
		return False

	def on_drag_data_get_data(self, treeview, context, selection, target_id, etime):
		"""will implement in subclass"""
		pass

	def on_drag_data_received_data(self, treeview, context, x, y, selection, info, etime):
		"""will implement in subclass"""
		pass

	def __add_columns(self):
		column = gtk.TreeViewColumn(self.type)
		column.set_spacing(5)

		renderer = gtk.CellRendererPixbuf()
		column.pack_start(renderer, False)
		column.set_attributes(renderer, pixbuf = COLUMN_ICON)

		renderer = gtk.CellRendererText()
		column.pack_start(renderer, True)
		column.set_attributes(renderer, text = COLUMN_TEMPINFO)

		self.append_column(column)

class EnableTemplate(TemplateList):
	"""The treeview to display the enable templates"""
	type = _("Enabled Templates")

	def __init__(self):
		TemplateList.__init__(self)
		self.create_model()

	def on_drag_data_get_data(self, treeview, context, selection, target_id, etime):
		treeselection = self.get_selection()
		model, iter = treeselection.get_selected()
		data = model.get_value(iter, COLUMN_FILE)
		selection.set(selection.target, 8, data)

	def on_drag_data_received_data(self, treeview, context, x, y, selection, info, etime):
		model = treeview.get_model()
		data = gnomevfs.format_uri_for_display(selection.data.strip())

		if os.path.basename(data) not in os.listdir(self.userdir):
			shutil.copy(data, self.userdir)
			data = os.path.join(self.userdir, os.path.basename(data))
		
		drop_info = treeview.get_dest_row_at_pos(x, y)

		icontheme = gtk.icon_theme_get_default()
		icon = ui.icon_lookup(icontheme, 
				None,
				data)

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

	def create_model(self):
		model = self.get_model()
		model.clear()

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

class DisableTemplate(TemplateList):
	"""The treeview to display the system template"""
	type = _("Disabled Templates")

	def __init__(self):
		TemplateList.__init__(self)
		self.create_model()

	def on_drag_data_get_data(self, treeview, context, selection, target_id, etime):
		treeselection = self.get_selection()
		model, iter = treeselection.get_selected()
		data = model.get_value(iter, COLUMN_FILE)
		selection.set(selection.target, 8, data)

	def on_drag_data_received_data(self, treeview, context, x, y, selection, info, etime):
		model = treeview.get_model()
		data = gnomevfs.format_uri_for_display(selection.data.strip())

		#if the item comes form userdir, delete or move it
		if '/'.join([dir for dir in data.split('/')[:4]]) == self.userdir:
			if os.path.basename(data) in os.listdir(self.systemdir):
				os.remove(data)
			else:
				shutil.move(data, self.systemdir)
			data = os.path.join(self.systemdir, os.path.basename(data))


		if os.path.basename(data) not in os.listdir(self.systemdir):
			shutil.copy(data, self.systemdir)
			data = os.path.join(self.systemdir, os.path.basename(data))
			
		drop_info = treeview.get_dest_row_at_pos(x, y)

		icontheme = gtk.icon_theme_get_default()
		icon = ui.icon_lookup(icontheme, 
				None,
				data)

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

	def create_model(self):
		model = self.get_model()
		model.clear()

		icontheme = gtk.icon_theme_get_default()

		for file in filter(lambda i: i not in os.listdir(self.userdir), os.listdir(self.systemdir)):
			filename = os.path.join(self.systemdir, file)
			icon = ui.icon_lookup(icontheme, 
					None,
					filename)

			pixbuf = icontheme.load_icon(icon[0], 32, 0)

			iter = model.append()
			model.set(iter,
				COLUMN_ICON, pixbuf,
				COLUMN_TEMPINFO, os.path.splitext(file)[0],
				COLUMN_FILE, filename)

class Templates(TweakPage, AbstractTempates):
        """Freedom added your docmuent templates"""
        def __init__(self, parent = None):
                TweakPage.__init__(self)

		self.default = DefaultTemplates()
		self.config_test()

		self.set_title(_("Manage your templates"))
		self.set_description(_("You can freely manage your document templates.\nDrag and Drop from file manager is supported.\nIt will be added to your righ-click menu: Create Document.\n"))

		hbox = gtk.HBox(False, 10)
		self.pack_start(hbox)

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		hbox.pack_start(sw)

		tl = EnableTemplate()
		sw.add(tl)

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		hbox.pack_start(sw)

		tl = DisableTemplate()
		sw.add(tl)

		hbox = gtk.HBox(False, 0)
		self.pack_start(hbox, False, False, 10)

		button = gtk.Button(_("Rebuild the system templates"))
		button.connect("clicked", self.on_rebuild_clicked, tl)
		hbox.pack_end(button, False, False, 5)

	def on_rebuild_clicked(self, widget, tl):
		dialog = MessageDialog(_("This will delete all the disabled templates, continue?"), title = _("Warning"), type = gtk.MESSAGE_WARNING)
		if dialog.run() == gtk.RESPONSE_YES:
			self.default.remove()
			self.default.create()
			tl.create_model()
		dialog.destroy()

	def config_test(self):
		if not os.path.exists(self.systemdir):
			self.default.create()

if __name__ == "__main__":
	win = gtk.Window()
	win.connect('destroy', lambda *w: gtk.main_quit())
        win.set_title("Document Templates")
        win.set_default_size(650, 400)
        win.set_border_width(8)

        win.add(Templates())

        win.show_all()
	gtk.main()	
