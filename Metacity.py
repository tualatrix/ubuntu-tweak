import pygtk
pygtk.require('2.0')
import gtk
import os
import gobject
import gettext

from Widgets import GConfCheckButton, ItemBox, EntryBox, HScaleBox, ComboboxItem

class Metacity(gtk.VBox):
	"""Some options about Metacity Window Manager"""
	def __init__(self):
		gtk.VBox.__init__(self)

		box = ItemBox(_("<b>Metacity Window Decorate Options</b>"), (
			GConfCheckButton(_("Use metacity theme"), "/apps/gwd/use_metacity_theme"),
			GConfCheckButton(_("Metacity theme active window opacity shade"), "/apps/gwd/metacity_theme_active_shade_opacity"),
			HScaleBox(_("Metacity active opacity"), 0, 1, "/apps/gwd/metacity_theme_active_opacity", digits = 2),
			GConfCheckButton(_("Metacity theme opacity shade"), "/apps/gwd/metacity_theme_shade_opacity"),
			HScaleBox(_("Metacity theme opacity"), 0, 1, "/apps/gwd/metacity_theme_opacity", digits = 2),
			ComboboxItem(_("Title bar mouse wheel action"), [_("No action"), _("Shade")], ["none", "shade"], "/apps/gwd/mouse_wheel_action")
			))

		self.pack_start(box, False, False, 0)
