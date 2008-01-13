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

