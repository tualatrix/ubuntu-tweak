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

from Widgets import GConfCheckButton, ItemBox

gettext.install("ubuntu-tweak", unicode = True)

lockdown_keys = \
[
	"/desktop/gnome/lockdown/disable_command_line",
	"/desktop/gnome/lockdown/disable_lock_screen",
	"/desktop/gnome/lockdown/disable_printing",
	"/desktop/gnome/lockdown/disable_print_setup",
	"/desktop/gnome/lockdown/disable_save_to_disk",
	"/desktop/gnome/lockdown/disable_user_switching",
]

lockdown_names = \
[
	_("Disable \"Run Application\" dialog (Alt+F2)"),
	_("Disable Lock Screen"),
	_("Disable Printing"),
	_("Disable Print Setup"),
	_("Disable Save To Disk"),
	_("Disable User Switching"),
]

class LockDown(gtk.VBox):
        """Lock down some function"""

        def __init__(self):
                gtk.VBox.__init__(self)

		box = ItemBox(_("<b>System Security options</b>"), ())
		for key in lockdown_keys:
			button = GConfCheckButton(lockdown_names[lockdown_keys.index(key)], key)
			box.vbox.pack_start(button, False, False, 0)

		self.pack_start(box, False, False, 0)
