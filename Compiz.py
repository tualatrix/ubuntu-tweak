import pygtk
pygtk.require("2.0")
import gtk
import gettext
import gconf

from Widgets import GConfCheckButton, ItemBox

gettext.install("ubuntu-tweak", unicode = True)

keys_of_plugins_with_edge = \
[
	"/apps/compiz/plugins/expo/allscreens/options/expo_edge",
	"/apps/compiz/plugins/scale/allscreens/options/initiate_edge",
	"/apps/compiz/plugins/scale/allscreens/options/initiate_all_edge",
]

names_of_plugins_with_edge = \
[
	"expo",
	"initiate",
	"initiate_all",
]

class Compiz(gtk.VBox):
	def combo_box_changed_cb(self, widget, edge):
		if widget.previous:
			self.change_edge(widget, edge)
		else:
			self.add_edge(widget, edge)
			
	def change_edge(self, widget, edge):
		previous = widget.previous
		i = names_of_plugins_with_edge.index(previous)

		self.remove_edge(keys_of_plugins_with_edge[i], edge)
		self.add_edge(widget, edge)	

	def add_edge(self, widget, edge):
		i = widget.get_active()
		if i == 3:
			widget.previous = None
		else:
			if i == 0:
				if not self.get_active_plugin_with_name("expo"):
					self.set_active("expo", True)
			if i == 1 or i == 2:
				if not self.get_active_plugin_with_name("scale"):
					self.set_active("scale", True)
			self.add_edge_base(keys_of_plugins_with_edge[i], edge)
			widget.previous = names_of_plugins_with_edge[i]

	def add_edge_base(self, element, edge):
		client = gconf.client_get_default()
		edge_list = client.get_list(element, gconf.VALUE_STRING)
		edge_list.append(edge)
		client.set_list(element, gconf.VALUE_STRING, edge_list)
			
	def remove_edge(self, element, edge):
		client = gconf.client_get_default()
		edge_list = client.get_list(element, gconf.VALUE_STRING)
		edge_list.remove(edge)
		client.set_list(element, gconf.VALUE_STRING, edge_list)

	def create_edge_combo_box(self, edge):
		combobox = gtk.combo_box_new_text()
		combobox.append_text(_("Expo"))
		combobox.append_text(_("Pick Windows"))
		combobox.append_text(_("Pick All Windows"))
		combobox.append_text("-")
		combobox.set_active(3)
		combobox.previous = None

		list = self.get_active_plugins()
		client = gconf.client_get_default()

		if not client.get_string("/apps/compiz/plugins/expo/allscreens/options/expo_key"):
			client.set_string("/apps/compiz/plugins/expo/allscreens/options/expo_button", "Button0")
			client.set_int("/apps/compiz/plugins/expo/allscreens/options/expo_edgebutton", 0)
			client.set_string("/apps/compiz/plugins/expo/allscreens/options/expo_key", "<Super>e")

		for element in keys_of_plugins_with_edge:
			edge_list = client.get_list(element, gconf.VALUE_STRING)

			if edge in edge_list:
				combobox.set_active(keys_of_plugins_with_edge.index(element))
				combobox.previous = names_of_plugins_with_edge[keys_of_plugins_with_edge.index(element)]

		combobox.connect("changed", self.combo_box_changed_cb, edge)
		return combobox

	def create_wobbly_effect_checkbutton(self, label, key):
		button = gtk.CheckButton(label) 
		button.connect("toggled", self.wobbly_checkbutton_toggled_cb, key)
		client = gconf.client_get_default()

		if self.get_active_plugin_with_name("wobbly"):
			value = client.get(key)

			if value.type == gconf.VALUE_INT:
				map_effect = value.get_int()
				match = client.get_string("/apps/compiz/plugins/wobbly/screen0/options/map_window_match")

				if map_effect == 1 and match.__len__() >= 4:
					button.set_active(True)

			elif value.type == gconf.VALUE_BOOL:
				if value.get_bool():
					button.set_active(True)

			elif value.type == gconf.VALUE_STRING:
				match = value.get_string()

				if match.__len__() >= 4:
					button.set_active(True)

		return button
	def wobbly_checkbutton_toggled_cb(self, widget, data = None):
		client = gconf.client_get_default()

		if widget.get_active():
			self.set_active("wobbly", True)
			value = client.get(data)

			if value.type == gconf.VALUE_INT:
				client.set_int(data, 1)
				client.set_string("/apps/compiz/plugins/wobbly/screen0/options/map_window_match","Splash | DropdownMenu | PopupMenu | Tooltip | Notification | Combo | Dnd | Unknown")
			elif value.type == gconf.VALUE_BOOL:
				client.set_bool(data, True)
			elif value.type == gconf.VALUE_STRING:
				client.set_string(data, "Toolbar | Menu | Utility | Dialog | Normal | Unknown")
		else:
			self.set_active("wobbly", False)
			value = client.get(data)

			if value.type == gconf.VALUE_INT:
				client.set_int(data, 0)
			elif value.type == gconf.VALUE_BOOL:
				client.set_bool(data, False)
			elif value.type == gconf.VALUE_STRING:
				client.set_string(data, "")

	def create_opacity_menu_checkbutton(self):
		button = gtk.CheckButton(_("Opacity Menu"))
		client = gconf.client_get_default()
		match_list = self.get_active_opacity("matches")
		value_list = self.get_active_opacity("values")

		for element in match_list:
			for value in value_list:
				if element.find("Menu") and value < 100:
					button.set_active(True)
		button.connect("toggled", self.opacity_checkbutton_toggled_cb)
		return button

	def opacity_checkbutton_toggled_cb(self, widget, data = None):
		client = gconf.client_get_default()
		bool = widget.get_active()
		match_list = self.get_active_opacity("matches")
		value_list = self.get_active_opacity("values")

		if bool:
			match_list.append("Tooltip | Menu | PopupMenu | DropdownMenu")
			client.set_list("/apps/compiz/general/screen0/options/opacity_matches", gconf.VALUE_STRING, match_list)
			value_list.append(90)
			client.set_list("/apps/compiz/general/screen0/options/opacity_values", gconf.VALUE_INT, value_list)
		else:
			match_list.remove("Tooltip | Menu | PopupMenu | DropdownMenu")
			client.set_list("/apps/compiz/general/screen0/options/opacity_matches", gconf.VALUE_STRING, match_list)
			value_list.remove(90)
			client.set_list("/apps/compiz/general/screen0/options/opacity_values", gconf.VALUE_INT, value_list)
			
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

		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(wallpaper, 160, 100)
		image = gtk.image_new_from_pixbuf(pixbuf)
		hbox.pack_start(image, False, False, 0)
		
		vbox = gtk.VBox(False, 0)
		hbox.pack_start(vbox, False, False, 0)
		
		combobox = self.create_edge_combo_box("TopRight")
		vbox.pack_start(combobox, False, False, 0)

		combobox = self.create_edge_combo_box("BottomRight")
		vbox.pack_end(combobox, False, False, 0)

		return hbox

	def create_snap_window_checkbutton(self, label):
		checkbutton = gtk.CheckButton(label)
		checkbutton.set_active(self.get_active_plugin_with_name("snap"))
		checkbutton.connect("toggled", self.snap_checkbutton_toggled_cb)

		return checkbutton
	def snap_checkbutton_toggled_cb(self, widget, data = None):
		self.set_active("snap", widget.get_active())

	def set_active(self, name, bool):
		client = gconf.client_get_default()
		if bool:
			list = self.get_active_plugins()
			list.append(name)
		else:
			list = self.get_active_plugins()
			list.remove(name)
		client.set_list("/apps/compiz/general/allscreens/options/active_plugins", gconf.VALUE_STRING, list)
			
	def get_active_plugin_with_name(self, name):
		return name in self.get_active_plugins()

	def get_active_plugins(self):
		client = gconf.client_get_default()
		return client.get_list("/apps/compiz/general/allscreens/options/active_plugins", gconf.VALUE_STRING)

	def get_active_opacity(self, type):
		client = gconf.client_get_default()
		if type == "matches":
			return client.get_list("/apps/compiz/general/screen0/options/opacity_matches", gconf.VALUE_STRING)
		if type == "values":
			return client.get_list("/apps/compiz/general/screen0/options/opacity_values", gconf.VALUE_INT)

	def __init__(self):
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

		button1 = self.create_snap_window_checkbutton(_("Snapping Windows(DON'T USE with Wobbly Windows)"))
		button2 = self.create_wobbly_effect_checkbutton(_("Maximize Effect"), "/apps/compiz/plugins/wobbly/screen0/options/maximize_effect")
		button3 = self.create_wobbly_effect_checkbutton(_("Wobbly Windows"),"/apps/compiz/plugins/wobbly/screen0/options/move_window_match")

		box = ItemBox(_("<b>Window Effects</b>"), (button1, button2, button3))
		self.pack_start(box, False, False, 0)

		button1 = self.create_opacity_menu_checkbutton()
		button2 = self.create_wobbly_effect_checkbutton(_("Wobbly Menu"), "/apps/compiz/plugins/wobbly/screen0/options/map_effect")

		box = ItemBox(_("<b>Menu Effects</b>"), (button1, button2))
		self.pack_start(box, False, False, 0)
