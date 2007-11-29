import pygtk
pygtk.require("2.0")
import gtk
import gconf

class GConfCheckButton(gtk.CheckButton):
	"""Create a check button with GConf function"""
	def value_changed(self, client, id, entry, data = None):
		client = gconf.client_get_default()
		value = client.get_value(self.key)
		if type(value) == bool:
			if value == True:
				self.set_active(True)
			if value == False:
				self.set_active(False)

	def toggled(self, widget, data = None):
		client = gconf.client_get_default()
		if self.get_active():
			client.set_bool(self.key, True)
		else:
			client.set_bool(self.key, False)

	def __init__(self, label, key, dir = None, extra = None):
		self.key = key
		client = gconf.client_get_default()
		value = client.get(key)
		if dir:
			client.add_dir(dir,gconf.CLIENT_PRELOAD_NONE)
			client.notify_add(key, self.value_changed)
		
		gtk.CheckButton.__init__(self)
		self.set_label(label)
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
			self.connect("toggled", extra, self.key)
		else:
			self.connect("toggled", self.toggled)
