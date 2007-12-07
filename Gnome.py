import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext

from Widgets import GConfCheckButton, ItemBox, ComboboxItem

gettext.install("ubuntu-tweak", unicode = True)

class Gnome(gtk.VBox):
	"""GNOME Settings"""

	def __init__(self):
		gtk.VBox.__init__(self)

		box = ItemBox(_("<b>GNOME Panel and Menu</b>"), (
			GConfCheckButton(_("Confirm before remove panel"), "/apps/panel/global/confirm_panel_remove"),
			GConfCheckButton(_("Complete lockdown of the Panel "), "/apps/panel/global/locked_down"),
			GConfCheckButton(_("Show Input Method menu in the right-click"), "/desktop/gnome/interface/show_input_method_menu"),
			GConfCheckButton(_("Show Unicode Method menu in the right-click"), "/desktop/gnome/interface/show_unicode_menu"),
			ComboboxItem(_("Notification-daemon popup location"), [_("Top Left"), _("Top Right"), _("Bottom Left"), _("Bottom Right")], ["top_left", "top_right", "bottom_left", "bottom_right"], "/apps/notification-daemon/popup_location")
			))
		self.pack_start(box, False, False, 0)

