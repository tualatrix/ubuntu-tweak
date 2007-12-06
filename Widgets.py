import pygtk
pygtk.require("2.0")
import gtk
import gconf

import pygtk
pygtk.require("2.0")
import gtk
import gconf

class GConfCheckButton(gtk.CheckButton):

	def value_changed(self, client, id, entry, data = None):
		client = gconf.client_get_default()
		value = client.get_value(data)

		if type(value) == bool:
			if value:
				self.set_active(True)
			else:
				self.set_active(False)

	def button_toggled(self, widget, data = None):
		client = gconf.client_get_default()

		if self.get_active():
			client.set_bool(data, True)
		else:
			client.set_bool(data, False)

	def __init__(self, label, key, extra = None):
		gtk.CheckButton.__init__(self)
		self.set_label(label)

		client = gconf.client_get_default()
		dir = "/".join(key.split("/")[0: -1])
		client.add_dir(dir,gconf.CLIENT_PRELOAD_NONE)
		client.notify_add(key, self.value_changed, key)

		value = client.get(key)

		if value:
			if value.type == gconf.VALUE_BOOL:
				if value.get_bool():
					self.set_active(True)
				else:
					self.set_active(False)
					
			elif value.type == gconf.VALUE_STRING:
				if value.get_string():
					self.set_active(True)
				else:
					self.set_active(False)

		if extra:
			self.connect("toggled", extra, key)
		else:
			self.connect("toggled", self.button_toggled, key)

class ItemBox(gtk.VBox):

	def __init__(self, title, widgets = None):
		gtk.VBox.__init__(self)
		self.set_border_width(5)
		
		label = gtk.Label()
		label.set_markup(title)
		label.set_alignment(0, 0)
		self.pack_start(label, False, False, 0)

		hbox = gtk.HBox(False, 5)
		hbox.set_border_width(5)
		self.pack_start(hbox, True, False, 0)

		label = gtk.Label(" ")
		hbox.pack_start(label, False, False, 0)

		self.vbox = gtk.VBox(False, 0)
		hbox.pack_start(self.vbox, True, True, 0)

		if widgets:
			if widgets.__len__() < 2:
				if type(widgets[0]) == GConfCheckButton:
					self.vbox.pack_start(widgets[0], False, False, 0)
				else:
					self.add(widgets[0])
			else:
				for widget in widgets:
					self.vbox.pack_start(widget, False, False, 0)

class EntryBox(gtk.HBox):
	def __init__(self, label, text):
		gtk.HBox.__init__(self)

		label = gtk.Label(label)
                self.pack_start(label, False, False,10)
                entry = gtk.Entry()
                entry.set_text(text)
                entry.set_editable(False)
		entry.set_size_request(300, -1)
                self.pack_end(entry, False, False, 0)
