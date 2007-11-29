import pygtk
pygtk.require("2.0")
import gtk
import gettext
import gconf

from gconfcheckbutton import GConfCheckButton

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

class CompizPage(gtk.VBox):
	def __combo_box_changed_cb(self, widget, edge):
		if widget.previous:
			self.__change_edge(widget, edge)
		else:
			self.__add_edge(widget, edge)
			
	def __change_edge(self, widget, edge):
		previous = widget.previous
		i = names_of_plugins_with_edge.index(previous)

		if i == 0:
			if not self.__get_active_plugin_with_name("expo"):
				self.__set_active("expo", True)
			self.__remove_edge(keys_of_plugins_with_edge[0], edge)
			self.__add_edge(widget, edge)
		else:
			if not self.__get_active_plugin_with_name("scale"):
				self.__set_active("scale", True)
			self.__remove_edge(keys_of_plugins_with_edge[i], edge)
			self.__add_edge(widget, edge)	

	def __add_edge(self, widget, edge):
		i = widget.get_active()
		if i == 3:
			widget.previous = None
		else:
			self.__add_edge_base(keys_of_plugins_with_edge[i], edge)
			widget.previous = names_of_plugins_with_edge[i]

	def __add_edge_base(self, element, edge):
		client = gconf.client_get_default()
		edge_list = client.get_list(element, gconf.VALUE_STRING)
		edge_list.append(edge)
		client.set_list(element, gconf.VALUE_STRING, edge_list,)
			
	def __remove_edge(self, element, edge):
		client = gconf.client_get_default()
		edge_list = client.get_list(element, gconf.VALUE_STRING)
		edge_list.remove(edge)
		client.set_list(element, gconf.VALUE_STRING, edge_list)

	def __create_edge_combo_box(self, edge):
		combobox = gtk.combo_box_new_text()
		combobox.append_text(_("Expo"))
		combobox.append_text(_("Pick Windows"))
		combobox.append_text(_("Pick All Windows"))
		combobox.append_text("-")
		combobox.set_active(3)
		combobox.previous = None

		list = self.__get_active_plugins()
		client = gconf.client_get_default()
		for element in keys_of_plugins_with_edge:
			edge_list = client.get_list(element, gconf.VALUE_STRING)

			if edge in edge_list:
				combobox.set_active(keys_of_plugins_with_edge.index(element))
				combobox.previous = names_of_plugins_with_edge[keys_of_plugins_with_edge.index(element)]

		combobox.connect("changed", self.__combo_box_changed_cb, edge)

		return combobox

	def __create_edge_setting(self):
		frame = gtk.Frame(_("Edge Setting"))
		frame.set_border_width(5)
		
		vbox = gtk.VBox(False, 5)
		vbox.set_border_width(5)
		frame.add(vbox)
		
		label = gtk.Label(_("Setting the action when you put your cursor in the screen edge"))
		label.set_alignment(0, 0)
		vbox.pack_start(label, False, False, 0)

		hbox = gtk.HBox(False, 0)
		vbox.pack_start(hbox, False, False, 0)

		vbox = gtk.VBox(False, 0)
		hbox.pack_start(vbox, False, False, 0)

		combobox = self.__create_edge_combo_box("TopLeft")
		vbox.pack_start(combobox, False, False, 0)

		combobox = self.__create_edge_combo_box("BottomLeft")
		vbox.pack_end(combobox, False, False, 0)

		client = gconf.client_get_default()
		wallpaper = client.get_string("/desktop/gnome/background/picture_filename")

		pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(wallpaper, 160, 100)
		image = gtk.image_new_from_pixbuf(pixbuf)
		hbox.pack_start(image, False, False, 0)
		
		vbox = gtk.VBox(False, 0)
		hbox.pack_start(vbox, False, False, 0)
		
		combobox = self.__create_edge_combo_box("TopRight")
		vbox.pack_start(combobox, False, False, 0)

		combobox = self.__create_edge_combo_box("BottomRight")
		vbox.pack_end(combobox, False, False, 0)

		return frame

	def __create_checkbutton_snap_window(self, label):
		checkbutton = gtk.CheckButton(label)
		checkbutton.set_active(self.__get_active_plugin_with_name("snap"))
		checkbutton.connect("toggled", self.__snap_checkbutton_toggled_cb)

		return checkbutton
	def __snap_checkbutton_toggled_cb(self, widget, data = None):
		self.__set_active("snap", widget.get_active())

	def __set_active(self, name, bool):
		client = gconf.client_get_default()
		if bool:
			list = self.__get_active_plugins()
			list.append(name)
		else:
			list = self.__get_active_plugins()
			list.remove(name)
		client.set_list("/apps/compiz/general/allscreens/options/active_plugins", gconf.VALUE_STRING, list)
			
	def __get_active_plugin_with_name(self, name):
		return name in self.__get_active_plugins()

	def __get_active_plugins(self):
		client = gconf.client_get_default()
		return client.get_list("/apps/compiz/general/allscreens/options/active_plugins", gconf.VALUE_STRING)

	def __get_active_opacity(self, type):
		client = gconf.client_get_default()
		if type == "matches":
			return client.get_list("/apps/compiz/general/screen0/options/opacity_matches", gconf.VALUE_STRING)
		if type == "values":
			return client.get_list("/apps/compiz/general/screen0/options/opacity_values", gconf.VALUE_INT)

	def __init__(self):
		gtk.VBox.__init__(self)
		self.set_border_width(5)

		self.pack_start(self.__create_edge_setting(), False, False, 0)

		button = self.__create_checkbutton_snap_window(_("Snapping Windows(DON'T USE with Wobbly Windows)"))
		self.pack_start(button, False, False, 0)
