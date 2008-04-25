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

from Constants import *
from Widgets import  TablePack
from Factory import Factory

gettext.install(App, unicode = True)

class Gnome(gtk.VBox):
	"""GNOME Settings"""

	def __init__(self, parent = None):
		gtk.VBox.__init__(self)

		box = TablePack(_("<b>GNOME Panel and Menu</b>"), [
			[Factory.create("gconfcheckbutton", _("Confirm before remove panel"), "confirm_panel_remove")],
			[Factory.create("gconfcheckbutton", _("Complete lockdown of the Panel "), "locked_down")],
			[Factory.create("gconfcheckbutton", _("Enable panel animations"), "enable_animations")],
			[Factory.create("gconfcheckbutton", _("Show Input Method menu in the right-click"), "show_input_method_menu")],
			[Factory.create("gconfcheckbutton", _("Show Unicode Method menu in the right-click"), "show_unicode_menu")],
			[gtk.Label(_("Notification-daemon popup location")), Factory.create("gconfcombobox", "popup_location", [_("Top Left"), _("Top Right"), _("Bottom Left"), _("Bottom Right")], ["top_left", "top_right", "bottom_left", "bottom_right"])]
			])
		self.pack_start(box, False, False, 0)

if __name__ == "__main__":
	from Utility import Test
	Test(Gnome)
