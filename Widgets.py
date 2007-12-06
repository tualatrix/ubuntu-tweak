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
		
		if title:
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

class HScaleBox(gtk.HBox):

	def hscale_value_changed_cb(self, widget, data = None):
		client = gconf.client_get_default()
		value = client.get(data)
		if value.type == gconf.VALUE_INT:
			client.set_int(data, int(widget.get_value()))
		elif value.type == gconf.VALUE_FLOAT:
			client.set_float(data, widget.get_value())

	def __init__(self, label, min, max, key, digits = 0):
		gtk.HBox.__init__(self)
		self.pack_start(gtk.Label(label), False, False, 0)
		
		hscale = gtk.HScale()
		hscale.set_size_request(150, -1)
		hscale.set_range(min, max)
		hscale.set_digits(digits)
		hscale.set_value_pos(gtk.POS_RIGHT)
		self.pack_end(hscale, False, False, 0)
		hscale.connect("value-changed", self.hscale_value_changed_cb, key)

		client = gconf.client_get_default()
		value = client.get(key)

		if value.type == gconf.VALUE_INT:
			hscale.set_value(client.get_int(key))
		elif value.type == gconf.VALUE_FLOAT:
			hscale.set_value(client.get_float(key))
