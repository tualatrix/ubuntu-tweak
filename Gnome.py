import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext

from Widgets import GConfCheckButton, ItemBox

gettext.install("ubuntu-tweak", unicode = True)

gnome_keys = \
[
	"/apps/panel/global/enable_animations",
	"/desktop/gnome/interface/enable_animations",
	"/apps/panel/global/locked_down",
	"/desktop/gnome/interface/show_input_method_menu",
	"/desktop/gnome/interface/show_unicode_menu"
]

keys_name = \
[
	_("Enable GNOME Animations Panel"),
	_("Enable GNOME Animations Effect"),
	_("Complete lockdown of the Panel "),
	_("Show Input Method menu in the right-click"),
	_("Show Unicode Method menu in the right-click"),
]

class Gnome(gtk.VBox):
	"""GNOME Settings"""

	def __init__(self):
		gtk.VBox.__init__(self)

		button1 = GConfCheckButton(keys_name[0], gnome_keys[0])
		button2 = GConfCheckButton(keys_name[1], gnome_keys[1])
		button3 = GConfCheckButton(keys_name[2], gnome_keys[2])
		button4 = GConfCheckButton(keys_name[3], gnome_keys[3])
		button5 = GConfCheckButton(keys_name[4], gnome_keys[4])

		box = ItemBox(_("<b>GNOME Animations</b>"), (button1, button2, button3, button4, button5))

		self.pack_start(box, False, False, 0)
