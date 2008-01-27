#!/usr/bin/env python
# coding: utf-8

import os
import gtk
import shutil
import gettext
import gobject
from xdg.DesktopEntry import DesktopEntry
from Widgets import ItemBox

gettext.install("ubuntu-tweak", unicode = True)

(
	COLUMN_ACTIVE,
	COLUMN_PROGRAM,
	COLUMN_PATH,
) = range(3)

class AutoStartDialog(gtk.Dialog):
	"""The dialog used to add or edit the startup item"""
	def __init__(self, desktopentry = None):
		gtk.Dialog.__init__(self)
		self.set_icon_from_file("pixmaps/ubuntu-tweak.png")

		lbl1 = gtk.Label()
		lbl1.set_markup(_("<b>Name:</b>"));
		lbl2 = gtk.Label()
		lbl2.set_markup(_("<b>Command:</b>"));
		lbl3 = gtk.Label()
		lbl3.set_markup(_("<b>Comment:</b>"));

		self.pm_name = gtk.Entry ();
		self.pm_cmd = gtk.Entry ();
		self.pm_comment = gtk.Entry ();

		if desktopentry:
			self.set_title(_("Edit Startup Program"))
			self.pm_name.set_text(desktopentry.getName())
			self.pm_cmd.set_text(desktopentry.getExec())
			self.pm_comment.set_text(desktopentry.getComment())
		else:
			self.set_title(_("New Startup Program"))

		button = gtk.Button(_("_Browse..."))
		button.connect("clicked", self.on_choose_program)
		
		hbox = gtk.HBox(False, 5)
		hbox.pack_start(self.pm_cmd)
		hbox.pack_start(button, False, False, 0)

		table = gtk.Table(3, 2)
		table.attach(lbl1, 0, 1, 0, 1, ypadding = 10)
		table.attach(lbl2, 0, 1, 1, 2, ypadding = 10)
		table.attach(lbl3, 0, 1, 2, 3, ypadding = 10)
		table.attach(self.pm_name, 1, 2, 0, 1)
		table.attach(hbox, 1, 2, 1, 2)
		table.attach(self.pm_comment, 1, 2, 2, 3)

		self.vbox.pack_start(table)

		self.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
		self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)

		self.set_default_response(gtk.RESPONSE_OK)

		self.show_all()

	def on_choose_program(self, widget, data = None):
		dialog = gtk.FileChooserDialog(_("Choose a Program"), action = gtk.FILE_CHOOSER_ACTION_OPEN, buttons = (gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

		if dialog.run() == gtk.RESPONSE_ACCEPT:
			self.pm_cmd.set_text(dialog.get_filename())
		dialog.destroy()

class AutoStartItem(gtk.TreeView):
	"""The autostart item list, loading from userdir and systemdir"""
	userdir = os.path.join(os.path.expanduser("~"), ".config/autostart")
	systemdir = "/etc/xdg/autostart"

	def __init__(self, list = None):
		gtk.TreeView.__init__(self)

		self.useritems = map(lambda path: "%s/%s" % (self.userdir, path), os.listdir(self.userdir))
		self.systemitems = map(lambda path: "%s/%s" % (self.systemdir, path), filter(lambda i: i not in os.listdir(self.userdir), os.listdir(self.systemdir)))

		model = gtk.ListStore(
			gobject.TYPE_BOOLEAN,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING)

		self.set_model(model)
		self.__create_model()

		self.__add_columns()
		self.set_rules_hint(True)
		self.set_size_request(180, -1)

	def update_items(self, all = None):
		"""The 'all' parameter used to show the hide item"""
		self.useritems = map(lambda path: "%s/%s" % (self.userdir, path), os.listdir(self.userdir))
		self.systemitems = map(lambda path: "%s/%s" % (self.systemdir, path), filter(lambda i: i not in os.listdir(self.userdir), os.listdir(self.systemdir)))
		self.__create_model(all)

	def __create_model(self, all = None):
		model = self.get_model()
		model.clear()

		allitems = []
		allitems.extend(self.useritems)
		allitems.extend(self.systemitems)

		for item in allitems:
			desktopentry = DesktopEntry(item)

			if desktopentry.get("Hidden"):
				if not all:
					continue
			iter = model.append()
			enable = desktopentry.get("X-GNOME-Autostart-enabled")
			if enable == "false":
				enable = False
			else:
				enable = True
			
			name = desktopentry.getName()
			comment = desktopentry.getComment()
			if not comment:
				comment = _("None description")
			description = "<b>%s</b>\n%s" % (name, comment)
			model.set(iter,
				COLUMN_ACTIVE, enable,
				COLUMN_PROGRAM, description,
				COLUMN_PATH, item)

	def __add_columns(self):
		model = self.get_model()

		renderer = gtk.CellRendererToggle()
		renderer.connect("toggled", self.enabled_toggled, model)
		column = gtk.TreeViewColumn(_("Enabled"), renderer, active = COLUMN_ACTIVE)
		self.append_column(column)

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn(_("Program"))
		column.pack_start(renderer, True)
		column.add_attribute(renderer, "markup", COLUMN_PROGRAM)
		self.append_column(column)

	def enabled_toggled(self, cell, path, model):
		iter = model.get_iter((int(path),))
		active = model.get_value(iter, COLUMN_ACTIVE)
		path = model.get_value(iter, COLUMN_PATH)

		if path[1:4] == 'etc':
			shutil.copy(path, self.userdir)
			path = os.path.join(self.userdir, os.path.basename(path))
			desktopentry = DesktopEntry(path)
			desktopentry.set("X-GNOME-Autostart-enabled", "false")
			desktopentry.write()
			model.set(iter, COLUMN_PATH, path)
		else:
			if active:
				desktopentry = DesktopEntry(path)
				desktopentry.set("X-GNOME-Autostart-enabled", "false")
				desktopentry.write()
			else:
				if os.path.basename(path) in os.listdir(self.systemdir):
					os.remove(path)
					path = os.path.join(self.systemdir, os.path.basename(path))
					model.set(iter, COLUMN_PATH, path)
				else:
					desktopentry = DesktopEntry(path)
					desktopentry.set("X-GNOME-Autostart-enabled", "true")
					desktopentry.set("Hidden", "false")
					desktopentry.write()

		active =  not active

		model.set(iter, COLUMN_ACTIVE, active)

class AutoStart(gtk.VBox):
	"""The box pack the autostart list"""
	def __init__(self):
		gtk.VBox.__init__(self)

		vbox = gtk.VBox(False, 0)
		vbox.set_border_width(5)
		self.pack_start(vbox)

		label = gtk.Label()
		label.set_markup(_("<b>Enable or Disable the autostart program.</b>"))
		label.set_alignment(0, 0)
		vbox.pack_start(label, False, False, 0)

		hbox = gtk.HBox(False, 10)
		vbox.pack_start(hbox, True, True, 10)

		checkbutton = gtk.CheckButton(_("Show all runable program"))
		checkbutton.connect("toggled", self.show_all_program)
		vbox.pack_start(checkbutton, False, False, 0)

		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		hbox.pack_start(sw)

		self.treeview = AutoStartItem()
		sw.add(self.treeview)
		
		vbox = gtk.VBox(False, 10)
		hbox.pack_start(vbox, False, False, 0)

		button = gtk.Button(stock = gtk.STOCK_ADD)
		button.connect("clicked", self.on_add_item, self.treeview)
		vbox.pack_start(button, False, False, 0)

		button = gtk.Button(stock = gtk.STOCK_REMOVE)
		button.connect("clicked", self.on_remove_item, self.treeview)
		vbox.pack_start(button, False, False, 0)

		button = gtk.Button(stock = gtk.STOCK_EDIT)
		button.connect("clicked", self.on_edit_item, self.treeview)
		vbox.pack_start(button, False, False, 0)

	def show_all_program(self, widget, data = None):
		if widget.get_active():
			self.treeview.update_items(all = True)
		else:
			self.treeview.update_items()

	def on_add_item(self, widget, treeview):
		dialog = AutoStartDialog()
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			path = os.path.join(treeview.userdir, os.path.basename(dialog.pm_cmd.get_text()) + ".desktop")
			desktopentry = DesktopEntry(path)
			desktopentry.set("Name", dialog.pm_name.get_text())
			desktopentry.set("Exec", dialog.pm_cmd.get_text())
			desktopentry.set("Comment", dialog.pm_comment.get_text())
			desktopentry.set("Type", "Application")
			desktopentry.set("Version", "1.0")
			desktopentry.set("X-GNOME-Autostart-enabled", "true")
			desktopentry.write()
			treeview.update_items()
		dialog.destroy()

	def on_remove_item(self, widget, treeview):
		model, iter = treeview.get_selection().get_selected()

		path = model.get_value(iter, COLUMN_PATH)
		if path[1:4] == "etc":
			shutil.copy(path, treeview.userdir)
			desktopentry = DesktopEntry(os.path.join(treeview.userdir, os.path.basename(path)))
		else:
			desktopentry = DesktopEntry(path)
		desktopentry.set("Hidden", "true")
		desktopentry.set("X-GNOME-Autostart-enabled", "false")
		desktopentry.write()

		treeview.update_items()

	def on_edit_item(self, widget, treeview):
		model, iter = treeview.get_selection().get_selected()

		path = model.get_value(iter, COLUMN_PATH)
		if path[1:4] == "etc":
			shutil.copy(path, treeview.userdir)
			path = os.path.join(treeview.userdir, os.path.basename(path))
		dialog = AutoStartDialog(DesktopEntry(path))
		response =  dialog.run()
		if response == gtk.RESPONSE_OK:
			desktopentry = DesktopEntry(path)
			desktopentry.set("Name", dialog.pm_name.get_text(), locale = True)
			desktopentry.set("Exec", dialog.pm_cmd.get_text(), locale = True)
			desktopentry.set("Comment", dialog.pm_comment.get_text(), locale = True)
			desktopentry.write()
			treeview.update_items()
		dialog.destroy()

if __name__ == "__main__":
	win = gtk.Window()
	win.connect('destroy', lambda *w: gtk.main_quit())
        win.set_title("AutoStart")
        win.set_default_size(650, 400)
        win.set_border_width(8)

	startup = AutoStart()
        win.add(startup)

        win.show_all()
	gtk.main()
