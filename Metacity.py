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

		box = ItemBox(_("<b>Window Decorate Effect</b>"), (
			GConfCheckButton(_("Use metacity theme"), "/apps/gwd/use_metacity_theme"),
			GConfCheckButton(_("Metacity theme active window opacity shade"), "/apps/gwd/metacity_theme_active_shade_opacity"),
			HScaleBox(_("Active window opacity level"), 0, 1, "/apps/gwd/metacity_theme_active_opacity", digits = 2),
			GConfCheckButton(_("Metacity theme opacity shade"), "/apps/gwd/metacity_theme_shade_opacity"),
			HScaleBox(_("Window shade opacity level"), 0, 1, "/apps/gwd/metacity_theme_opacity", digits = 2),
			))
		self.pack_start(box, False, False, 0)

		box = ItemBox(_("<b>Window Titlebar Action</b>"),(
			ComboboxItem(_("Title bar mouse wheel action"), [_("None"), _("Roll up")], ["none", "shade"], "/apps/gwd/mouse_wheel_action"),
			ComboboxItem(_("Title bar Double-click action"), [_("None"), _("Maximize"), _("Minimize"), _("Roll up"), _("Lower"), _("Menu")], ["none", "toggle_maximize", "minimize", "toggle_shade", "lower", "menu"], "/apps/metacity/general/action_double_click_titlebar"),
			ComboboxItem(_("Title bar Middle-click action"), [_("None"), _("Maximize"), _("Minimize"), _("Roll up"), _("Lower"), _("Menu")], ["none", "toggle_maximize", "minimize", "toggle_shade", "lower", "menu"], "/apps/metacity/general/action_middle_click_titlebar"),
			ComboboxItem(_("Title bar Right-click action"), [_("None"), _("Maximize"), _("Minimize"), _("Roll up"), _("Lower"), _("Menu")], ["none", "toggle_maximize", "minimize", "toggle_shade", "lower", "menu"], "/apps/metacity/general/action_right_click_titlebar"),
			))
		self.pack_start(box, False, False, 0)
