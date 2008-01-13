#!/usr/bin/env python

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import pygtk
pygtk.require('2.0')
import gtk
import os
import gobject
import gettext

from Widgets import GConfCheckButton, ItemBox, EntryBox, HScaleBox, ComboboxItem
from Computer import DISTRIB

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

		if DISTRIB != "feisty":
			box = ItemBox(_("<b>Window Titlebar Action</b>"),(
				ComboboxItem(_("Title bar mouse wheel action"), [_("None"), _("Roll up")], ["none", "shade"], "/apps/gwd/mouse_wheel_action"),
				ComboboxItem(_("Title bar Double-click action"), [_("None"), _("Maximize"), _("Minimize"), _("Roll up"), _("Lower"), _("Menu")], ["none", "toggle_maximize", "minimize", "toggle_shade", "lower", "menu"], "/apps/metacity/general/action_double_click_titlebar"),
				ComboboxItem(_("Title bar Middle-click action"), [_("None"), _("Maximize"), _("Minimize"), _("Roll up"), _("Lower"), _("Menu")], ["none", "toggle_maximize", "minimize", "toggle_shade", "lower", "menu"], "/apps/metacity/general/action_middle_click_titlebar"),
				ComboboxItem(_("Title bar Right-click action"), [_("None"), _("Maximize"), _("Minimize"), _("Roll up"), _("Lower"), _("Menu")], ["none", "toggle_maximize", "minimize", "toggle_shade", "lower", "menu"], "/apps/metacity/general/action_right_click_titlebar"),
				))
			self.pack_start(box, False, False, 0)
